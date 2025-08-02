# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'testeVLiGv.ui'
## Created by: Qt User Interface Compiler version 5.x.x
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTimer, QUrl, Qt, QTime, pyqtSignal)  # QTime 추가
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QApplication,QMessageBox,QLabel, QMainWindow, QPushButton,
    QSizePolicy, QStackedWidget, QStatusBar, QWidget)
import threading

import output
import sendkakaottt
import serial
import pynmea2
import time

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()

class Ui_MainWindow(object):

    def __init__(self):
        self.gpsLat = 0.0  # GPS 위도의 초기 값 설정 (float)
        self.gpsLng = 0.0  # GPS 경도의 초기 값 설정 (float)
        self.serial = None
        self.try_open_serial_port()

    def try_open_serial_port(self):
        try:
            self.serial = serial.Serial('/dev/ttyS0', 9600, timeout=1)
            threading.Timer(1, self.getGPS).start()
        except Exception as e:
            print("GPS 데이터 수신 오류:", str(e))
            self.show_message_box("GPS 데이터 수신 오류", str(e))
            threading.Timer(5, self.try_open_serial_port).start()

    def getGPS(self):
        if self.serial:
            data = self.serial.readline().decode('utf-8').strip()
            try:
                lat_str, lng_str = data.split(",")
                self.gpsLat = float(lat_str)
                self.gpsLng = float(lng_str)
                print(f"GPS 데이터 수신: 위도 {self.gpsLat}, 경도 {self.gpsLng}")
            except ValueError:
                print("GPS 데이터 수신 오류: 올바르지 않은 형식")

        threading.Timer(1, self.getGPS).start()

    def send_location_message(self):
        message = f"현재 위치는 위도: {self.gpsLat}, 경도: {self.gpsLng}입니다."
        print("메시지 전송:", message)

    def update_map_location(self):
        # 네이버 지도와 연동하여 실시간 위치를 업데이트하는 코드 예시
        # 네이버 지도 API에 위도와 경도를 float 타입으로 전달
        # 예: naver_map.update_location(self.gpsLat, self.gpsLng)
        pass

    def show_message_box(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1920, 1080)
        MainWindow.setMinimumSize(QSize(1920, 1080))
        MainWindow.setMaximumSize(QSize(1920, 1080))

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(0, -30, 1920, 1080))
        self.stackedWidget.setMinimumSize(QSize(1920, 1080))
        self.stackedWidget.setMaximumSize(QSize(1920, 1080))
        self.stackedWidget.setStyleSheet(u"background-image: url(:/background.png);")

        self.page = QWidget()
        self.page.setObjectName(u"page")

        self.webEngineView_2 = QWebEngineView(self.page)
        self.webEngineView_2.setObjectName(u"webEngineView_2")
        self.webEngineView_2.setGeometry(QRect(380, 150, 1461, 861))
        self.webEngineView_2.setUrl(
            QUrl("file:///C:/Users/pjo77/OneDrive/Desktop/uimaker/myipkey1.html"))
        
        self.pushButton_4 = QPushButton(self.page)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setGeometry(QRect(70, 460, 231, 111))
        self.pushButton_4.setStyleSheet(u"background-image: url(:/map.png);")
        self.pushButton_4.clicked.connect(self.send_kakao_message)

        self.pushButton_5 = QPushButton(self.page)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setGeometry(QRect(70, 150, 231, 111))
        self.pushButton_5.setStyleSheet(u"background-image: url(:/emrcall.png);")

        self.pushButton_6 = QPushButton(self.page)
        self.pushButton_6.setObjectName(u"pushButton_6")
        self.pushButton_6.setGeometry(QRect(70, 780, 231, 111))
        self.pushButton_6.setStyleSheet(u"background-image: url(:/speed.png);")

        self.label = QLabel(self.page)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(490, 20, 331, 91))
        font = QFont()
        font.setPointSize(36)
        self.label.setFont(font)

        self.label_2 = QLabel(self.page)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(0, -10, 291, 151))
        self.label_2.setStyleSheet(u"background-image: url(:/title.png);")
        self.label_2.setScaledContents(True)

        self.set = ClickableLabel(self.page)  # ClickableLabel로 변경
        self.set.setObjectName(u"set")
        self.set.setGeometry(QRect(1840, 50, 61, 61))
        self.set.setStyleSheet(u"background-image: url(:/setting.png);")
        self.set.setPixmap(QPixmap(u":/setting.png"))
        self.set.setScaledContents(True)

        self.stackedWidget.addWidget(self.page)

        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")

        self.pushButton = QPushButton(self.page_2)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(200, 40, 1521, 261))
        font1 = QFont()
        font1.setPointSize(20)
        self.pushButton.setFont(font1)

        self.pushButton_2 = QPushButton(self.page_2)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setGeometry(QRect(200, 370, 1521, 301))
        self.pushButton_2.setFont(font1)

        self.pushButton_3 = QPushButton(self.page_2)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setGeometry(QRect(200, 750, 1521, 271))
        self.pushButton_3.setFont(font1)

        self.stackedWidget.addWidget(self.page_2)

        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")

        self.swver = QLabel(self.page_3)
        self.swver.setObjectName(u"swver")
        self.swver.setGeometry(QRect(330, 40, 191, 51))
        font2 = QFont()
        font2.setPointSize(16)
        self.swver.setFont(font2)

        self.reboot = QLabel(self.page_3)
        self.reboot.setObjectName(u"reboot")
        self.reboot.setGeometry(QRect(330, 150, 81, 51))
        self.reboot.setFont(font2)

        self.noti = QLabel(self.page_3)
        self.noti.setObjectName(u"noti")
        self.noti.setGeometry(QRect(330, 250, 131, 41))
        self.noti.setFont(font2)

        self.customer = QLabel(self.page_3)
        self.customer.setObjectName(u"customer")
        self.customer.setGeometry(QRect(330, 340, 141, 41))
        self.customer.setFont(font2)

        self.stackedWidget.addWidget(self.page_3)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)

        self.set.clicked.connect(self.goToPage3)  # 클릭 시 goToPage3 호출

        # 버튼 클릭 연결
        self.pushButton_6.clicked.connect(self.goToPage2)
        self.pushButton.clicked.connect(self.goToPage)
        self.pushButton_2.clicked.connect(self.goToPage)
        self.pushButton_3.clicked.connect(self.goToPage)

        # 시계 업데이트
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateClock)
        self.timer.start(1000)
        self.updateClock()

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.pushButton_4.setText("")
        self.pushButton_5.setText("")
        self.pushButton_6.setText("")
        self.label.setText("")
        self.label_2.setText("")
        self.set.setText("")
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\uc18d\ub3c4 : 1\ub2e8\uacc4", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"\uc18d\ub3c4 : 2\ub2e8\uacc4", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"\uc18d\ub3c4 : 3\ub2e8\uacc4", None))
        self.swver.setText(QCoreApplication.translate("MainWindow", u"s/w version : 0.0.1", None))
        self.reboot.setText(QCoreApplication.translate("MainWindow", u"\uc7ac\ubd80\ud305", None))
        self.noti.setText(QCoreApplication.translate("MainWindow", u"\uc54c\ub9bc", None))
        self.customer.setText(QCoreApplication.translate("MainWindow", u"\uace0\uac1d\uc13c\ud130", None))

    def updateClock(self):
        current_time = QTime.currentTime().toString('HH:mm:ss')
        self.label.setText(current_time)

    def goToPage2(self):
        self.stackedWidget.setCurrentIndex(1)  # 페이지 2

    def goToPage(self):
        self.stackedWidget.setCurrentIndex(0)  # 페이지 1

    def goToPage3(self):
        self.stackedWidget.setCurrentIndex(2)  # 페이지 3

    def send_kakao_message(self):
        sendkakaottt.send_kakao_message("UwZLmEB13Umqk3uFuz3g8CltdTpc5FsZAAAAAgo8IlEAAAGSmokpYMTTXs9KIG_V", str(self.gpsLat), str(self.gpsLng))

    def send_gps_message(self):
        message = f"현재 위치: 위도 {self.gpsLat}, 경도 {self.gpsLng}"
        self.send_kakao_message("YOUR_ACCESS_TOKEN", message)

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())