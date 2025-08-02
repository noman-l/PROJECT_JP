# -*- coding: utf-8 -*-
from PyQt5.QtCore import QCoreApplication, QDate, QTime, QTimer, QUrl, Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QStackedWidget, QStatusBar, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
import serial
import speech_recognition as sr
import subprocess
import sys
import sendkakao_ver_3
import phonecall


class GPSWorker(QThread):
    gps_signal = pyqtSignal(float, float)

    def __init__(self, port):
        super().__init__()
        self.serial_port = port
        self.serial_conn = None

    def run(self):
        try:
            self.serial_conn = serial.Serial(self.serial_port, 9600, timeout=1)
            while True:
                data = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                if data.startswith('$GNGGA'):
                    try:
                        parts = data.split(',')
                        lat_str, lng_str = parts[2], parts[4]
                        gpsLat = float(lat_str[:2]) + float(lat_str[2:]) / 60.0 if lat_str else 0.0
                        if parts[3] == 'S':
                            gpsLat = -gpsLat
                        gpsLng = float(lng_str[:3]) + float(lng_str[3:]) / 60.0 if lng_str else 0.0
                        if parts[5] == 'W':
                            gpsLng = -gpsLng
                        self.gps_signal.emit(gpsLat, gpsLng)
                    except (IndexError, ValueError):
                        continue
        except Exception as e:
            print("GPS 데이터 수신 오류:", str(e))


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.resize(800, 480)
        self.setMinimumSize(QSize(800, 480))
        self.setMaximumSize(QSize(800, 480))

        # Initialize UI components
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.initUI()

        # Set up GPS worker
        self.gps_worker = GPSWorker('/dev/ttyAMA0')
        self.gps_worker.gps_signal.connect(self.update_gps)
        self.gps_worker.start()

        # Timer for updating time display
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)  # Update every second

    def initUI(self):
        # Set up stacked widget for different pages
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(0, 10, 800, 480)

        # Main page setup
        self.page = QWidget()

        # Google Maps widget on main page
        self.webEngineView_2 = QWebEngineView(self.page)
        self.webEngineView_2.setGeometry(340, 140, 421, 301)
        self.webEngineView_2.setUrl(QUrl('http://localhost:8000/map.html'))

        # Clock label
        self.label = QLabel(self.page)
        self.label.setGeometry(270, 10, 361, 51)
        font = QFont()
        font.setPointSize(24)
        self.label.setFont(font)

        # GPS status label
        self.label_gps = QLabel(self.page)
        self.label_gps.setGeometry(10, 420, 300, 50)
        self.label_gps.setFont(font)

        # Buttons on page
        self.pushButton_4 = QPushButton(self.page)
        self.pushButton_4.setGeometry(30, 220, 231, 111)
        self.pushButton_4.setStyleSheet("background-image: url(:/map.png);")
        self.pushButton_4.clicked.connect(self.send_kakao_message)

        self.pushButton_5 = QPushButton(self.page)
        self.pushButton_5.setGeometry(30, 110, 231, 101)
        self.pushButton_5.setStyleSheet("background-image: url(:/emrcall.png);")
        self.pushButton_5.clicked.connect(self.go_to_page_4)

        self.pushButton_6 = QPushButton(self.page)
        self.pushButton_6.setGeometry(30, 340, 231, 111)
        self.pushButton_6.setStyleSheet("background-image: url(:/speed.png);")
        self.pushButton_6.clicked.connect(self.go_to_page_2)

        # Title label
        self.label_2 = QLabel(self.page)
        self.label_2.setGeometry(0, -60, 291, 151)
        self.label_2.setFont(font)

        # Settings button
        self.set = QLabel(self.page)
        self.set.setGeometry(700, 40, 61, 61)
        self.set.setStyleSheet("background-image: url(:/setting.png);")
        self.set.setPixmap(QPixmap(":/setting.png"))
        self.set.setScaledContents(True)
        self.set.mousePressEvent = self.go_to_page_3

        self.label_4 = QLabel(self.page)
        self.label_4.setGeometry(0, 30, 370, 61)
        self.label_4.setFont(font)

        self.pushButton_speech = QPushButton(self.page)
        self.pushButton_speech.setGeometry(270, 370, 60, 60)
        self.pushButton_speech.setStyleSheet("background-color: rgb(173,214,214)")
        self.pushButton_speech.clicked.connect(self.recognize_speech)
        self.stackedWidget.addWidget(self.page)

        # Page 2 setup
        self.page_2 = QWidget()
        font1 = QFont()
        font1.setPointSize(20)
        self.label_3 = QLabel(self.page_2)
        self.label_3.setGeometry(270, 10, 361, 51)
        self.label_3.setFont(font)

        self.pushButton = QPushButton(self.page_2)
        self.pushButton.setGeometry(90, 60, 601, 81)
        self.pushButton.setFont(font1)
        self.pushButton.clicked.connect(self.speed_0_status)

        self.pushButton_2 = QPushButton(self.page_2)
        self.pushButton_2.setGeometry(90, 150, 601, 81)
        self.pushButton_2.setFont(font1)
        self.pushButton_2.clicked.connect(self.speed_1_status)

        self.pushButton_3 = QPushButton(self.page_2)
        self.pushButton_3.setGeometry(90, 240, 601, 81)
        self.pushButton_3.setFont(font1)
        self.pushButton_3.clicked.connect(self.speed_2_status)

        self.pushButton_7 = QPushButton(self.page_2)
        self.pushButton_7.setGeometry(90, 330, 601, 81)
        self.pushButton_7.setFont(font1)
        self.pushButton_7.clicked.connect(self.speed_3_status)

        self.stackedWidget.addWidget(self.page_2)

        # Page 3 setup
        self.page_3 = QWidget()
        font2 = QFont()
        font2.setPointSize(16)

        self.swver = QLabel(self.page_3)
        self.swver.setGeometry(330, 40, 191, 51)
        self.swver.setFont(font2)

        self.reboot = QPushButton(self.page_3)
        self.reboot.setGeometry(330, 150, 101, 51)
        self.reboot.setFont(font2)
        self.reboot.clicked.connect(self.reboot_program)

        self.noti = QLabel(self.page_3)
        self.noti.setGeometry(330, 250, 131, 41)
        self.noti.setFont(font2)

        self.customer = QLabel(self.page_3)
        self.customer.setGeometry(330, 340, 141, 41)
        self.customer.setFont(font2)

        self.pushButton_8 = QPushButton(self.page_3)
        self.pushButton_8.setGeometry(480, 370, 150, 51)
        self.pushButton_8.setFont(font2)
        self.pushButton_8.clicked.connect(self.go_to_page)
        self.stackedWidget.addWidget(self.page_3)

        # Page 4 setup
        self.page_4 = QWidget()
        self.pushButton_9 = QPushButton(self.page_4)
        self.pushButton_9.setGeometry(480, 370, 150, 51)
        self.pushButton_9.setFont(font2)
        self.pushButton_9.clicked.connect(self.go_to_page)

        self.pushButton_10 = QPushButton(self.page_4)
        self.pushButton_10.setGeometry(80, 60, 300, 81)
        self.pushButton_10.clicked.connect(self.call_112)
        self.pushButton_10.setFont(font2)

        self.pushButton_11 = QPushButton(self.page_4)
        self.pushButton_11.setGeometry(80, 170, 300, 81)
        self.pushButton_11.clicked.connect(self.call_119)
        self.pushButton_11.setFont(font2)

        self.pushButton_12 = QPushButton(self.page_4)
        self.pushButton_12.setGeometry(400, 60, 300, 81)
        self.pushButton_12.clicked.connect(self.call_nok)
        self.pushButton_12.setFont(font2)

        self.pushButton_13 = QPushButton(self.page_4)
        self.pushButton_13.setGeometry(400, 170, 300, 81)
        self.pushButton_13.setFont(font2)

        self.stackedWidget.addWidget(self.page_4)

        # Status bar
        self.setStatusBar(QStatusBar(self))

    def update_gps(self, lat, lng):
        self.label_gps.setText(f"위도 {lat}, 경도 {lng}")

    def update_clock(self):
        current_date = QDate.currentDate().toString('yy-MM-dd (ddd)')
        current_time = QTime.currentTime().toString('HH:mm:ss')
        self.label.setText(f"{current_date} {current_time}")

    def go_to_page_2(self):
        self.stackedWidget.setCurrentIndex(1)

    def go_to_page_4(self):
        self.stackedWidget.setCurrentIndex(3)

    def send_kakao_message(self):
        print(f"전송할 GPS 데이터: 위도 {self.gps_worker.gpsLat}, 경도 {self.gps_worker.gpsLng}")
        sendkakao_ver_3.send_kakao_message(
            "UwZLmEB13Umqk3uFuz3g8CltdTpc5FsZAAAAAgo8IlEAAAGSmokpYMTTXs9KIG_V",
            self.gps_worker.gpsLat,
            self.gps_worker.gpsLng
        )

    def recognize_speech(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            recognized_text = recognizer.recognize_google(audio, language="ko-KR")
            print(f"Recognized Speech: {recognized_text}")
            if recognized_text == "1단계":
                self.label_4.setText("속도 : 1단계")
            elif recognized_text == "2단계":
                self.label_4.setText("속도 : 2단계")
            elif recognized_text == "3단계":
                self.label_4.setText("속도 : 3단계")
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

    def reboot_program(self):
        python = sys.executable
        subprocess.Popen([python] + sys.argv)
        QCoreApplication.quit()

    def call_112(self):
        phonecall.call_112(self)

    def call_119(self):
        phonecall.call_119(self)

    def call_nok(self):
        phonecall.call_nok(self)

    def speed_0_status(self):
        self.label_4.setText("초기상태")

    def speed_1_status(self):
        self.label_4.setText("속도 : 1단계")

    def speed_2_status(self):
        self.label_4.setText("속도 : 2단계")

    def speed_3_status(self):
        self.label_4.setText("속도 : 3단계")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())
