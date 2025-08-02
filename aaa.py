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

import output
import socket
import subprocess
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 480)
        MainWindow.setMinimumSize(QSize(800, 480))
        MainWindow.setMaximumSize(QSize(800, 480))

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
        self.webEngineView_2.setUrl(QUrl("https://www.google.com/maps"))

        # Buttons on page
        self.pushButton_4 = QPushButton(self.page)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setGeometry(QRect(30, 220, 231, 111))
        self.pushButton_4.setStyleSheet("background-image: url(:/map.png);")

        self.pushButton_5 = QPushButton(self.page)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setGeometry(QRect(30, 110, 231, 101))
        self.pushButton_5.setStyleSheet("background-image: url(:/emrcall.png);")

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

        self.stackedWidget.addWidget(self.page)

        # Page 2
        self.page_2 = QWidget()
        self.page_2.setObjectName("page_2")

        font1 = QFont()
        font1.setPointSize(20)
        
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(270, 10, 361, 51))

        self.pushButton = QPushButton(self.page_2)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QRect(70, 80, 601, 81))
        self.pushButton.setFont(font1)
        self.pushButton.clicked.connect(self.go_to_page)  # Navigate back to page

        self.pushButton_2 = QPushButton(self.page_2)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setGeometry(QRect(70, 120, 601, 81))
        self.pushButton_2.setFont(font1)
        self.pushButton_2.clicked.connect(self.go_to_page)  # Navigate back to page

        self.pushButton_3 = QPushButton(self.page_2)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setGeometry(QRect(110, 240, 601, 81))
        self.pushButton_3.setFont(font1)
        self.pushButton_3.clicked.connect(self.go_to_page)  # Navigate back to page
        self.sound=QPushButton(self.page)
        self.sound.setObjectName("sound")
        self.sound.setGeometry(QRect(270,230,61,81))
        self.sound.setStyleSheet("background-color: blue;")
        self.sound.setText("sound")
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

        self.reboot = QLabel(self.page_3)
        self.reboot.setObjectName("reboot")
        self.reboot.setGeometry(QRect(330, 150, 81, 51))
        self.reboot.setFont(font2)

        self.noti = QLabel(self.page_3)
        self.noti.setObjectName("noti")
        self.noti.setGeometry(QRect(330, 250, 131, 41))
        self.noti.setFont(font2)

        self.customer = QLabel(self.page_3)
        self.customer.setObjectName("customer")
        self.customer.setGeometry(QRect(330, 340, 141, 41))
        self.customer.setFont(font2)

        self.stackedWidget.addWidget(self.page_3)

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
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "MainWindow", None))
        self.pushButton_4.setText("")
        self.pushButton_5.setText("")
        self.pushButton_6.setText("")
        self.label.setText("")
        self.label_2.setText("RooKie")
        #self.label_3.setText("")
        self.set.setText("")
        self.pushButton.setText(QCoreApplication.translate("MainWindow", "속도 : 1단계", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", "속도 : 2단계", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", "속도 : 3단계", None))
        self.swver.setText(QCoreApplication.translate("MainWindow", "s/w version : 0.0.1", None))
        self.reboot.setText(QCoreApplication.translate("MainWindow", "재부팅", None))
        self.noti.setText(QCoreApplication.translate("MainWindow", "알림", None))
        self.customer.setText(QCoreApplication.translate("MainWindow", "고객센터", None))

    # Method to update the clock
    def update_clock(self):
        current_date = QDate.currentDate().toString('yy-MM-dd (ddd)')
        current_time = QTime.currentTime().toString('HH:mm:ss')
        self.label.setText(f"{current_date} {current_time}")

    # Method to switch to page 2
    def go_to_page_2(self):
        self.stackedWidget.setCurrentIndex(1)

    # Method to switch to page 3 (settings page)
    def go_to_page_3(self, event):
        self.stackedWidget.setCurrentIndex(2)

    # Method to switch back to the main page
    def go_to_page(self):
        self.stackedWidget.setCurrentIndex(0)
    def start_sound_output(self):

        subprocess.run(["pactl", "set-default-sink", "bcm2835:0"])
        print("Sound output started on Raspberry Pi.")

    def stop_sound_output(self):

        subprocess.run(["pactl", "set-default-sink", "vc4-hdmi"])
        print("Sound output stopped on Raspberry Pi.")

    def toggle(self):
        if self.is_sound_on:
            self.stop_sound_output()
        else:    
            self,start_sound_output()
        self.is_sound_on = not self.is_sound_on

    def main():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("0.0.0.0", 5000)) 
        server_socket.listen(1)

        print("Server listening on port 5000...")
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")

            command = client_socket.recv(1024).decode("utf-8")
            if command == "START":
                start_sound_output()
            elif command == "STOP":
                stop_sound_output()

            client_socket.close()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
