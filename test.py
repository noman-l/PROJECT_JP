import os
import requests
import json
import socket
import serial
import time
import string
import pynmea2
from PyQt5.QtCore import (QCoreApplication, QDateTime, QMetaObject, QThread, QSize, QTimer, QUrl)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow, QPushButton, QStackedWidget, QStatusBar, QWidget)
import output
import jitest
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 480)
        MainWindow.setMinimumSize(QSize(800, 480))
        MainWindow.setMaximumSize(QSize(800, 480))

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.stackedWidget.setGeometry(0, 10, 800, 480)

        self.page = QWidget()
        self.page.setObjectName("page")
        self.webEngineView_2 = QWebEngineView(self.page)
        self.webEngineView_2.setObjectName("webEngineView_2")
        self.webEngineView_2.setGeometry(340, 140, 421, 301)
        self.webEngineView_2.setUrl(QUrl("https://www.google.com/maps"))

        self.pushButton_4 = QPushButton(self.page)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setGeometry(30, 220, 231, 111)
        self.pushButton_4.setStyleSheet("background-image: url(:/map.png);")
        self.pushButton_4.clicked.connect(jitest)



        self.pushButton_5 = QPushButton(self.page)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setGeometry(30, 110, 231, 101)
        self.pushButton_5.setStyleSheet("background-image: url(:/emrcall.png);")

        self.pushButton_6 = QPushButton(self.page)
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.setGeometry(30, 340, 231, 111)
        self.pushButton_6.setStyleSheet("background-image: url(:/speed.png);")
        self.pushButton_6.clicked.connect(self.go_to_page_2)

        self.label = QLabel(self.page)
        self.label.setObjectName("label")
        self.label.setGeometry(270, 10, 361, 51)
        font = QFont()
        font.setPointSize(24)
        self.label.setFont(font)

        self.set = QLabel(self.page)
        self.set.setObjectName("set")
        self.set.setGeometry(700, 40, 61, 61)
        self.set.setStyleSheet("background-image: url(:/setting.png);")
        self.set.setPixmap(QPixmap(":/setting.png"))
        self.set.setScaledContents(True)
        self.set.mousePressEvent = self.go_to_page_3

        self.stackedWidget.addWidget(self.page)

        self.page_2 = QWidget()
        self.page_2.setObjectName("page_2")

        font1 = QFont()
        font1.setPointSize(20)

        self.pushButton = QPushButton(self.page_2)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(70, 80, 601, 81)
        self.pushButton.setFont(font1)
        self.pushButton.clicked.connect(self.go_to_page)

        self.pushButton_2 = QPushButton(self.page_2)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setGeometry(70, 120, 601, 81)
        self.pushButton_2.setFont(font1)
        self.pushButton_2.clicked.connect(self.go_to_page)

        self.pushButton_3 = QPushButton(self.page_2)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setGeometry(110, 240, 601, 81)
        self.pushButton_3.setFont(font1)
        self.pushButton_3.clicked.connect(self.go_to_page)

        self.sound = QPushButton(self.page)
        self.sound.setObjectName("sound")
        self.sound.setGeometry(270, 230, 61, 81)
        self.sound.setStyleSheet("background-color: blue;")
        self.sound.setText("sound")
        self.sound.clicked.connect(self.start_server)

        self.stackedWidget.addWidget(self.page_2)

        self.page_3 = QWidget()
        self.page_3.setObjectName("page_3")

        font2 = QFont()
        font2.setPointSize(16)

        self.swver = QLabel(self.page_3)
        self.swver.setObjectName("swver")
        self.swver.setGeometry(330, 40, 191, 51)
        self.swver.setFont(font2)

        self.reboot = QLabel(self.page_3)
        self.reboot.setObjectName("reboot")
        self.reboot.setGeometry(330, 150, 81, 51)
        self.reboot.setFont(font2)

        self.noti = QLabel(self.page_3)
        self.noti.setObjectName("noti")
        self.noti.setGeometry(330, 250, 131, 41)
        self.noti.setFont(font2)

        self.customer = QLabel(self.page_3)
        self.customer.setObjectName("customer")
        self.customer.setGeometry(330, 340, 141, 41)
        self.customer.setFont(font2)

        self.stackedWidget.addWidget(self.page_3)

        MainWindow.setCentralWidget(self.centralwidget)

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.timer = QTimer(MainWindow)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "MainWindow", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", "Speed", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", "Page 2", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", "Back to Page 1", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", "Send GPS", None))

    def start_server(self):
        self.server_thread = ServerThread()
        self.server_thread.start()

    def go_to_page(self):
        self.stackedWidget.setCurrentIndex(0)

    def go_to_page_2(self):
        self.stackedWidget.setCurrentIndex(1)

    def go_to_page_3(self):
        self.stackedWidget.setCurrentIndex(2)

    def update_clock(self):
        now = QDateTime.currentDateTime()
        self.label.setText(now.toString('yyyy-MM-dd hh:mm:ss'))

    def refresh_access_token(self, refresh_token):
        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": "23996064e9c4fc796c5d57476a9318de",
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

    def send_kakao_message(self, access_token, message):
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        template_object = {
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": "https://www.example.com",
                "mobile_web_url": "https://www.example.com",
            },
            "button_title": "자세히 보기",
        }

        data = {
            "template_object": json.dumps(template_object),
        }

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            print("메시지 전송 성공")
        else:
            print("메시지 전송 실패:", response.json())

    def send_gps_message(self):
        try:
            ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
            while True:
                data = ser.readline().decode('ascii', errors='replace')
                if data.startswith('$GPGGA'):
                    msg = pynmea2.parse(data)
                    latitude = msg.latitude
                    longitude = msg.longitude
                    message = f"현재 위치: 위도 {latitude}, 경도 {longitude}"
                    self.send_kakao_message("YOUR_ACCESS_TOKEN", message)
                    break
                time.sleep(1)
        except Exception as e:
            print("GPS 데이터 수신 오류:", str(e))
        finally:
            ser.close()

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
