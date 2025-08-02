from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from flask import Flask, jsonify
from flask_cors import CORS
import threading
import sys
import requests
import json

# Flask 서버 설정
app = Flask(__name__)
CORS(app)

# GPS 데이터 (초기값)
gps_data = {"latitude": 37.6303483, "longitude": 126.8335345}


@app.route('/location')
def location():
    """현재 GPS 데이터를 반환"""
    return jsonify(gps_data)


def run_flask_app():
    """Flask 서버 실행"""
    app.run(host="127.0.0.1", port=8001)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("GPS Map and Kakao Integration")
        self.setGeometry(100, 100, 1024, 600)

        # 중앙 위젯 및 레이아웃
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # QWebEngineView를 사용하여 map.html 로드
        self.web_view = QWebEngineView(self)
        self.web_view.setUrl(QUrl("http://localhost:8000/map2.html"))  # map.html 파일 로드
        self.layout.addWidget(self.web_view)

        # 카카오 메시지 전송 버튼
        self.kakao_button = QPushButton("Send Kakao Message", self)
        self.kakao_button.clicked.connect(self.send_kakao_message)
        self.layout.addWidget(self.kakao_button)

    def send_kakao_message(self):
        """카카오 메시지 전송"""
        refresh_token = "MvVF9937EBBxh7YZt6z8a4WGwZfQsgZiAAAAAgo9c-wAAAGTQw5Hi8TTXs9KIG_V"  # 자신의 리프레시 토큰으로 대체
        access_token, new_refresh_token = self.refresh_access_token(refresh_token)

        if not access_token:
            print("카카오톡 액세스 토큰이 없습니다.")
            return

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        template_object = {
            "object_type": "text",
            "text": f"https://map.naver.com/v5/entry/address?lng={gps_data['longitude']}&lat={gps_data['latitude']}&title=내위치",
            "link": {
                "web_url": "https://www.example.com",
                "mobile_web_url": "https://www.example.com"
            },
            "button_title": "웹사이트로 가기"
        }

        data = {"template_object": json.dumps(template_object)}

        response = requests.post(
            "https://kapi.kakao.com/v2/api/talk/memo/default/send",
            headers=headers,
            data=data,
        )

        if response.status_code == 200:
            print("메시지가 성공적으로 전송되었습니다.")
        else:
            print("메시지 전송 실패:", response.json())

    def refresh_access_token(self, refresh_token):
        """리프레시 토큰으로 새로운 액세스 토큰 발급"""
        response = requests.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "refresh_token",
                "client_id": "23996064e9c4fc796c5d57476a9318de",
                "refresh_token": refresh_token,
            },
        )

        if response.status_code != 200:
            print("토큰 재발급 오류:", response.json())
            return None, None

        tokens = response.json()
        return tokens['access_token'], tokens.get('refresh_token', None)


def start_http_server():
    """로컬 HTTP 서버 시작"""
    import http.server
    import socketserver

    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8000), handler) as httpd:
        print("Serving HTTP on port 8000")
        httpd.serve_forever()


if __name__ == "__main__":
    # Flask 서버 쓰레드 실행
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()

    # HTTP 서버 쓰레드 실행
    http_server_thread = threading.Thread(target=start_http_server, daemon=True)
    http_server_thread.start()

    # PyQt 애플리케이션 실행
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
