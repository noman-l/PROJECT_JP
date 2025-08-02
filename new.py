# -*- coding: utf-8 -*-
from PyQt5.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                          QMetaObject, QObject, QPoint, QRect,
                          QSize, QTimer, QUrl, Qt, QTime, pyqtSignal)  # QTime 추가
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                         QFont, QFontDatabase, QGradient, QIcon,
                         QImage, QKeySequence, QLinearGradient, QPainter,
                         QPalette, QPixmap, QRadialGradient, QTransform)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QApplication, QLabel, QMainWindow, QPushButton,
                             QSizePolicy, QStackedWidget, QStatusBar, QWidget)
import bluetooth
import output
import speech_recognition as sr
import RPi.GPIO as GPIO
import subprocess
import sys
import sendkakao_ver_3
# import HX711
import time
import phonecall
import serial
import threading

# DT_PIN_1 = 23 # raspberry pi 16 pin
# SCK_PIN_1 = 11 # raspberry pi 23 pin
# DT_PIN_2 = 24 # raspberry pi 18 pin
# SCK_PIN_2 = 18 # raspberry pi 12 pin

# hx_1 = HX711.HX711(DT_PIN_1,SCK_PIN_1)
# hx_2 = HX711.HX711(DT_PIN_2,SCK_PIN_2)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.gpsLng = 0.0
        self.gpsLat = 0.0
        self.serial = None
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 480)
        MainWindow.setMinimumSize(QSize(800, 480))
        MainWindow.setMaximumSize(QSize(800, 480))

        self.try_open_serial_port()

        # Timer for updating time
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def try_open_serial_port(self):
        try:
            self.serial = serial.Serial('/dev/ttyS0', 9600, timeout=1)
            threading.Timer(1, self.getGPS).start()
        except Exception as e:
            print("GPS 데이터 수신 오류:", str(e))
            self.show_message_box("GPS 데이터 수신 오류", str(e))
            threading.Timer(5, self.try_open_serial_port).start()

    def getGPS(self):
        if self.serial and self.serial.is_open:
            data = self.serial.readline().decode('utf-8').strip()
            print(f"받은 데이터: {data}")
            try:
                if data.startswith('$GNGGA'):
                    parts = data.split(',')
                    if len(parts) > 4:  # 데이터가 충분한지 확인
                        lat_str = parts[2]  # 위도
                        lng_str = parts[4]  # 경도

                        # 위도 및 경도 변환
                        self.gpsLat = float(lat_str[:2]) + float(lat_str[2:]) / 60.0
                        if parts[3] == 'S':
                            self.gpsLat = -self.gpsLat  # 남위일 경우 음수

                        self.gpsLng = float(lng_str[:3]) + float(lng_str[3:]) / 60.0
                        if parts[5] == 'W':
                            self.gpsLng = -self.gpsLng  # 서경일 경우 음수

                        self.label_gps.setText(f"GPS 데이터: 위도 {self.gpsLat}, 경도 {self.gpsLng}")
                        print(f"GPS data receive: Lat {self.gpsLat}, lng {self.gpsLng}")
            except ValueError:
                print("GPS 데이터 수신 오류: 올바르지 않은 형식")
        threading.Timer(1, self.getGPS).start()

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.stackedWidget.setGeometry(QRect(0, 10, 800, 480))
        self.stackedWidget.setMinimumSize(QSize(800, 480))
        self.stackedWidget.setMaximumSize(QSize(800, 480))

        self.page = QWidget()
        self.page.setObjectName("page")
        self.webEngineView_2 = QWebEngineView(self.page)
        self.webEngineView_2.setObjectName("webEngineView_2")
        self.webEngineView_2.setGeometry(QRect(340, 140, 421, 301))

        self.webEngineView_2.setHtml('http://localhost:8000/map.html')

        # Buttons on page
        self.pushButton_4 = QPushButton(self.page)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setGeometry(QRect(30, 220, 231, 111))
        self.pushButton_4.setStyleSheet("background-image: url(:/map.png);")
        self.pushButton_4.clicked.connect(self.send_kakao_message)

        self.pushButton_5 = QPushButton(self.page)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setGeometry(QRect(30, 110, 231, 101))
        self.pushButton_5.setStyleSheet("background-image: url(:/emrcall.png);")
        self.pushButton_5.clicked.connect(self.go_to_page_4)  # Navigate to page_4

        self.pushButton_6 = QPushButton(self.page)
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.setGeometry(QRect(30, 340, 231, 111))
        self.pushButton_6.setStyleSheet("background-image: url(:/speed.png);")
        self.pushButton_6.clicked.connect(self.go_to_page_2)  # Navigate to page_2

        # Clock label on page
        self.label = QLabel(self.page)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(270, 10, 361, 51))
        font = QFont()
        font.setPointSize(24)
        self.label.setFont(font)

        # Title label
        self.label_2 = QLabel(self.page)
        self.label_2.setObjectName("label_2")
        self.label_2.setGeometry(QRect(0, -60, 291, 151))
        self.label_2.setFont(font)

        # Settings button
        self.set = QLabel(self.page)
        self.set.setObjectName("set")
        self.set.setGeometry(QRect(700, 40, 61, 61))
        self.set.setStyleSheet("background-image: url(:/setting.png);")
        self.set.setPixmap(QPixmap(":/setting.png"))
        self.set.setScaledContents(True)
        self.set.mousePressEvent = self.go_to_page_3  # Navigate to page_3 on click

        self.label_4 = QLabel(self.page)
        self.label_4.setObjectName("status")
        self.label_4.setGeometry(QRect(0, 30, 370, 61))
        self.label_4.setFont(font)

        self.pushButton_speech = QPushButton(self.page)
        self.pushButton_speech.setObjectName("speech_button")
        self.pushButton_speech.setGeometry(QRect(270, 370, 60, 60))
        self.pushButton_speech.setStyleSheet("background-color: rgb(173,214,214)")
        self.pushButton_speech.clicked.connect(self.recognize_speech)
        self.stackedWidget.addWidget(self.page)

        # Page 2
        self.page_2 = QWidget()
        self.page_2.setObjectName("page_2")

        font1 = QFont()
        font1.setPointSize(20)

        self.label_3 = QLabel(self.page_2)
        self.label_3.setObjectName("label_3")
        self.label_3.setGeometry(QRect(270, 10, 361, 51))
        self.label_3.setFont(font)

        self.pushButton = QPushButton(self.page_2)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QRect(90, 60, 601, 81))
        self.pushButton.setFont(font1)
        self.pushButton.clicked.connect(self.speed_0_status)  # Navigate back to page

        self.pushButton_2 = QPushButton(self.page_2)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setGeometry(QRect(90, 150, 601, 81))
        self.pushButton_2.setFont(font1)
        self.pushButton_2.clicked.connect(self.speed_1_status)  # Navigate back to page

        self.pushButton_3 = QPushButton(self.page_2)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setGeometry(QRect(90, 240, 601, 81))
        self.pushButton_3.setFont(font1)
        self.pushButton_3.clicked.connect(self.speed_2_status)  # Navigate back to page

        self.pushButton_7 = QPushButton(self.page_2)
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_7.setGeometry(QRect(90, 330, 601, 81))
        self.pushButton_7.setFont(font1)
        self.pushButton_7.clicked.connect(self.speed_3_status)  # Navigate back to page

        self.stackedWidget.addWidget(self.page_2)

        # Page 3
        self.page_3 = QWidget()
        self.page_3.setObjectName("page_3")

        font2 = QFont()
        font2.setPointSize(16)

        self.swver = QLabel(self.page_3)
        self.swver.setObjectName("swver")
        self.swver.setGeometry(QRect(330, 40, 191, 51))
        self.swver.setFont(font2)

        self.reboot = QPushButton(self.page_3)
        self.reboot.setObjectName("reboot")
        self.reboot.setGeometry(QRect(330, 150, 101, 51))
        self.reboot.setFont(font2)
        self.reboot.clicked.connect(self.reboot_program)

        self.noti = QLabel(self.page_3)
        self.noti.setObjectName("noti")
        self.noti.setGeometry(QRect(330, 250, 131, 41))
        self.noti.setFont(font2)

        self.customer = QLabel(self.page_3)
        self.customer.setObjectName("customer")
        self.customer.setGeometry(QRect(330, 340, 141, 41))
        self.customer.setFont(font2)

        self.pushButton_8 = QPushButton(self.page_3)
        self.pushButton_8.setObjectName("pushButton_8")
        self.pushButton_8.setGeometry(QRect(480, 370, 150, 51))
        self.pushButton_8.setFont(font2)
        self.pushButton_8.clicked.connect(self.go_to_page)  # Navigate back to page

        self.stackedWidget.addWidget(self.page_3)

        # page 4
        self.page_4 = QWidget()
        self.page_4.setObjectName("page_4")

        self.pushButton_9 = QPushButton(self.page_4)  # 뒤로가기
        self.pushButton_9.setObjectName("pushButton_9")
        self.pushButton_9.setGeometry(QRect(480, 370, 150, 51))
        self.pushButton_9.setFont(font2)
        self.pushButton_9.clicked.connect(self.go_to_page)

        self.pushButton_10 = QPushButton(self.page_4)  # 112
        self.pushButton_10.setObjectName("pushButton_10")
        self.pushButton_10.setGeometry(QRect(80, 60, 300, 81))
        self.pushButton_10.clicked.connect(self.call_112)
        self.pushButton_10.setFont(font2)

        self.pushButton_11 = QPushButton(self.page_4)  # 119
        self.pushButton_11.setObjectName("pushButton_11")
        self.pushButton_11.setGeometry(QRect(80, 170, 300, 81))
        self.pushButton_11.clicked.connect(self.call_119)
        self.pushButton_11.setFont(font2)

        self.pushButton_12 = QPushButton(self.page_4)  # 보호자
        self.pushButton_12.setObjectName("pushButton_12")
        self.pushButton_12.setGeometry(QRect(400, 60, 300, 81))
        self.pushButton_12.clicked.connect(self.call_nok)
        self.pushButton_12.setFont(font2)

        self.pushButton_13 = QPushButton(self.page_4)  # 끊기
        self.pushButton_13.setObjectName("pushButton_13")
        self.pushButton_13.setGeometry(QRect(400, 170, 300, 81))
        self.pushButton_13.setFont(font2)

        self.stackedWidget.addWidget(self.page_4)

        # self.initialize_hx711()

        MainWindow.setCentralWidget(self.centralwidget)

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(0)

        # Timer to update clock every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)  # Update every second

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton_4.setText("")
        self.pushButton_5.setText("")
        self.pushButton_6.setText("")
        self.label.setText("")
        self.label_2.setText("RooKie")
        self.label_3.setText("")
        self.label_4.setText("초기상태")
        self.set.setText("")
        self.pushButton.setText(
            QCoreApplication.translate("MainWindow", u"\uc18d\ub3c4 : \uc218\ub3d9\ubaa8\ub4dc", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"\uc18d\ub3c4 : 1단계", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"\uc18d\ub3c4 : 2단계", None))
        self.pushButton_7.setText(QCoreApplication.translate("MainWindow", u"\uc18d\ub3c4 : 3단계", None))
        self.pushButton_8.setText(QCoreApplication.translate("MainWindow", u"\ub4a4\ub85c\uac00\uae30", None))  # Back
        self.pushButton_9.setText(QCoreApplication.translate("MainWindow", u"\ub4a4\ub85c\uac00\uae30", None))  # Back
        self.pushButton_10.setText(QCoreApplication.translate("MainWindow", u"call 112", None))  # 112연결
        self.pushButton_11.setText(QCoreApplication.translate("MainWindow", u"call 119", None))  # 119연결
        self.pushButton_12.setText(QCoreApplication.translate("MainWindow", u"call nok", None))  # 보호자연결
        self.pushButton_13.setText(QCoreApplication.translate("MainWindow", u"hang up the phone", None))  # 전화끊기
        self.pushButton_speech.setText(QCoreApplication.translate("MainWindow", u"음성\n인식", None))
        self.swver.setText(QCoreApplication.translate("MainWindow", "S/W Version : 0.0.1", None))
        self.reboot.setText(QCoreApplication.translate("MainWindow", "재부팅", None))
        self.noti.setText(QCoreApplication.translate("MainWindow", "알림", None))
        self.customer.setText(QCoreApplication.translate("MainWindow", "고객센터", None))

    # Method to update the clock
    def update_clock(self):
        current_date = QDate.currentDate().toString('yy-MM-dd (ddd)')
        current_time = QTime.currentTime().toString('HH:mm:ss')
        self.label.setText(f"{current_date} {current_time}")
        self.label_3.setText(f"{current_date} {current_time}")

    # Method to switch to page 2
    def go_to_page_2(self):
        self.stackedWidget.setCurrentIndex(1)

    # Method to switch to page 3 (settings page)
    def go_to_page_3(self, event):
        self.stackedWidget.setCurrentIndex(2)

    # Method to switch back to the main page
    def go_to_page(self):
        self.stackedWidget.setCurrentIndex(0)

    def go_to_page_4(self):
        self.stackedWidget.setCurrentIndex(3)

    def speed_0_status(self):
        self.label_4.setText("초기상태")
        self.pushButton.clicked.connect(self.go_to_page)

    def speed_1_status(self):
        self.label_4.setText("속도 : 1단계")
        self.pushButton_2.clicked.connect(self.go_to_page)

    def speed_2_status(self):
        self.label_4.setText("속도 : 2단계")
        self.pushButton_3.clicked.connect(self.go_to_page)

    def speed_3_status(self):
        self.label_4.setText("속도 : 3단계")
        self.pushButton_7.clicked.connect(self.go_to_page)

    def reboot_program(self):
        python = sys.executable
        subprocess.Popen([python] + sys.argv)

        QCoreApplication.quit()

    '''
    def initialize_hx711(self):
        hx_1.set_reading_format("MSB", "MSB")
        hx_1.set_reference_unit(1) # bo zung
        hx_1.reset()
        hx_1.tare() #yung zyum

        hx_2.set_reading_format("MSB", "MSB")
        hx_2.set_reference_unit(1) # bo zung
        hx_2.reset()
        hx_2.tare() # yung zyum
        print("hx711 setting good")

    def measure_weight(self):
        weight_1 = hx_1.get_weight(5)
        weight_2 = hx_2.get_weight(5)
        hx_1.power_down()
        hx_1.power_up()
        hx_2.power_down()
        hx_2.power_up()
'''

    def recognize_speech(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            print("Recognizing...")
            recognized_text = recognizer.recognize_google(audio, language="ko-KR")
            print(f"Recognized Speech: {recognized_text}")
            if (recognized_text == "1단계"):
                self.label_4.setText("속도 : 1단계")
            elif (recognized_text == "2단계"):
                self.label_4.setText("속도 : 2단계")
            elif (recognized_text == "3단계"):
                self.label_4.setText("속도 : 3단계")


        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

    def send_kakao_message(self):
        print(f"전송할 GPS 데이터: 위도 {self.gpsLat}, 경도 {self.gpsLng}")

        sendkakao_ver_3.send_kakao_message(
            "UwZLmEB13Umqk3uFuz3g8CltdTpc5FsZAAAAAgo8IlEAAAGSmokpYMTTXs9KIG_V",
            self.gpsLat,
            self.gpsLng
        )

    def call_112(self):
        phonecall.call_112(self)

    def call_119(self):
        phonecall.call_119(self)

    def call_nok(self):
        phonecall.call_nok(self)

    def hang_upself(self):
        phonecall.hang_up(self)


'''
    def connect_bluetooth(self):
        target_address = ""  
        port = 3  
        phone_number = ""  
        print("Searching for Bluetooth devices...")

        try:
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((target_address, port))
            print("Bluetooth connection successful!")


            sock.send(f"ATD{phone_number};\r")
            print(f"Calling {phone_number} ...")

            sock.close()

        except bluetooth.BluetoothError as e:
            print(f"Bluetooth connection failed: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")
'''

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())