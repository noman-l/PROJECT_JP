import sys
import socket
import serial
import pynmea2
from PyQt5.QtCore import QThread, pyqtSignal, QTime, QTimer
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QStackedWidget, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QUrl
import requests
import json
import output


class ServerThread(QThread):
    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', 12345))
        self.server_socket.listen(1)
        print("Server started, waiting for connections...")

        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Connection from {addr}")
            data = client_socket.recv(1024).decode()
            if data == "play_sound":
                print("Playing sound...")
            client_socket.close()

class GPSThread(QThread):
    gps_data_received = pyqtSignal(str)  # GPS 데이터를 UI로 보내기 위한 시그널

    def run(self):
        serialPort = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)
        while True:
            data = serialPort.readline().decode('ascii', errors='replace')
            if data:
                self.gps_data_received.emit(data)  # GPS 데이터를 시그널로 보냄

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi()

        # GPS 스레드 실행
        self.gps_thread = GPSThread()
        self.gps_thread.gps_data_received.connect(self.parseGPS)  # 시그널 연결
        self.gps_thread.start()

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(800, 480)
        self.setMinimumSize(800, 480)
        self.setMaximumSize(800, 480)

        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(0, 10, 800, 480)

        # 페이지 설정
        self.page = QWidget()
        self.stackedWidget.addWidget(self.page)

        self.webEngineView_2 = QWebEngineView(self.page)
        self.webEngineView_2.setGeometry(340, 140, 421, 301)
        self.webEngineView_2.setUrl(QUrl("https://www.google.com/maps"))

        self.label = QLabel(self.page)
        self.label.setGeometry(270, 10, 361, 51)
        font = self.label.font()
        font.setPointSize(24)
        self.label.setFont(font)

        self.sound = QPushButton(self.page)
        self.sound.setGeometry(270, 230, 61, 81)
        self.sound.setStyleSheet("background-color: blue;")
        self.sound.setText("Sound")
        self.sound.clicked.connect(self.start_server)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)

    def update_clock(self):
        current_time = QTime.currentTime().toString("hh:mm:ss")
        self.label.setText(current_time)

    def start_server(self):
        self.server_thread = ServerThread()
        self.server_thread.start()

    def parseGPS(self, data):
        if data.find('GGA') > 0:
            msg = pynmea2.parse(data)
            lat = self.convert_to_decimal_degrees(msg.lat, msg.lat_dir)
            lon = self.convert_to_decimal_degrees(msg.lon, msg.lon_dir)
            print(f"Latitude: {lat}, Longitude: {lon}")

            # 구글 맵에 새로운 위치 업데이트
            self.update_map(lat, lon)

    def convert_to_decimal_degrees(self, raw_value, direction):
        """NMEA 포맷의 위도/경도를 십진수 포맷으로 변환"""
        degrees = float(raw_value[:2])
        minutes = float(raw_value[2:])
        decimal_degrees = degrees + minutes / 60
        if direction in ['S', 'W']:
            decimal_degrees = -decimal_degrees
        return decimal_degrees

    def update_map(self, lat, lon):
        """JavaScript를 통해 구글 맵의 위치를 업데이트"""
        js_code = f"""
        var myLatLng = {{lat: {lat}, lng: {lon}}};
        map.setCenter(myLatLng);
        new google.maps.Marker({{
            position: myLatLng,
            map: map
        }});
        """
        self.webEngineView_2.page().runJavaScript(js_code)

    def refresh_access_token(refresh_token):
        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": "23996064e9c4fc796c5d57476a9318de",  # 본인의 앱 클라이언트 ID
            "refresh_token": refresh_token
        }

        response = requests.post(url, data=data)
        if response.status_code == 200:
            tokens = response.json()
            new_access_token = tokens['access_token']
            new_refresh_token = tokens['refresh_token']
            print("새로운 액세스 토큰:", new_access_token)
            print("새로운 리프레시 토큰:", new_refresh_token)
            return new_access_token, new_refresh_token
        else:
            print("토큰 재발급 오류:", response.json())
            return None, None

    # 카카오톡 메시지를 전송하는 함수
    def send_kakao_message(access_token):
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",  # x-www-form-urlencoded로 설정합니다.
        }

        # 템플릿 오브젝트를 JSON 형식으로 정의합니다.
        template_object = {
            "object_type": "text",
            "text": "안녕하세요! 이것은 KakaoTalk 메시지입니다.",
            "link": {
                "web_url": "https://www.example.com",
                "mobile_web_url": "https://www.example.com"
            },
            "button_title": "웹사이트로 가기"
        }

        # JSON 데이터를 문자열로 변환
        template_object_json = json.dumps(template_object)

        data = {
            "template_object": template_object_json  # 문자열로 설정
        }

        # data 파라미터를 사용하여 데이터를 전송합니다.
        response = requests.post(url, headers=headers, data=data)

        # 응답 확인
        if response.status_code == 200:
            print("메시지가 성공적으로 전송되었습니다.")
            return response  # 응답 객체를 반환
        else:
            print("메시지 전송 오류:", response.json())
            return None  # 오류 시 None 반환

    # 액세스 토큰 및 리프레시 토큰을 설정
    access_token = "HCNPkwyX-rwdwISJd3n896tH25yuj93EAAAAAQo8IlEAAAGSmokpZcTTXs9KIG_V"
    refresh_token = "UwZLmEB13Umqk3uFuz3g8CltdTpc5FsZAAAAAgo8IlEAAAGSmokpYMTTXs9KIG_V"  # 예시 리프레시 토큰

    # 메시지를 전송하려고 시도
    response = send_kakao_message(access_token)

    # 만약 메시지 전송이 실패하면 리프레시 토큰으로 새 액세스 토큰을 요청
    if response is None:  # 메시지 전송이 실패했을 때
        new_access_token, new_refresh_token = refresh_access_token(refresh_token)
        if new_access_token:
            send_kakao_message(new_access_token)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
