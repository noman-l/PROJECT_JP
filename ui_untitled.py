import serial
import threading
import pynmea2
import time
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication


class Ui_MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # UI 요소 초기화
        self.initUI()

        # GPS 좌표 변수
        self.gpsLat = 0.0
        self.gpsLng = 0.0

        # GPS 모듈 연결 시도
        try:
            self.serial = serial.Serial('/dev/ttyS0', 9600, timeout=1)
        except Exception as e:
            print("GPS 데이터 수신 오류:", str(e))

        # GPS 데이터 주기적으로 수신
        threading.Timer(1, self.getGPS).start()

    def initUI(self):
        # 위도와 경도를 표시할 QLabel을 생성
        self.latLabel = QLabel("위도: 0.0", self)
        self.latLabel.setGeometry(50, 50, 200, 30)

        self.lngLabel = QLabel("경도: 0.0", self)
        self.lngLabel.setGeometry(50, 100, 200, 30)

        # 메인 윈도우 설정
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('GPS 좌표 표시')
        self.show()

    def getGPS(self):
        while True:
            try:
                # GPS 데이터 수신
                data = self.serial.readline().decode('ascii', errors='replace')

                if data.startswith('$GPGGA'):  # NMEA GGA 문장으로 시작하는 경우
                    msg = pynmea2.parse(data)
                    self.gpsLat = msg.latitude
                    self.gpsLng = msg.longitude

                    # QLabel에 위도와 경도 업데이트
                    self.latLabel.setText(f"위도: {self.gpsLat}")
                    self.lngLabel.setText(f"경도: {self.gpsLng}")

                time.sleep(1)
            except Exception as e:
                print("GPS 데이터 수신 오류:", str(e))


# PyQt5 애플리케이션 실행
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = Ui_MainWindow()
    sys.exit(app.exec_())
