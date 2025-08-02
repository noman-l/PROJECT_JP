# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import resource_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(858, 548)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.background = QtWidgets.QLabel(self.centralwidget)
        self.background.setGeometry(QtCore.QRect(0, -10, 861, 541))
        self.background.setMinimumSize(QtCore.QSize(861, 541))
        self.background.setMaximumSize(QtCore.QSize(861, 541))
        self.background.setText("")
        self.background.setPixmap(QtGui.QPixmap(":/background/background.png"))
        self.background.setObjectName("background")
        self.btn1 = QtWidgets.QPushButton(self.centralwidget)
        self.btn1.setGeometry(QtCore.QRect(60, 110, 221, 71))
        self.btn1.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/button/btn1.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn1.setIcon(icon)
        self.btn1.setIconSize(QtCore.QSize(200, 100))
        self.btn1.setObjectName("btn1")
        self.btn2 = QtWidgets.QPushButton(self.centralwidget)
        self.btn2.setGeometry(QtCore.QRect(60, 340, 221, 71))
        self.btn2.setText("")
        self.btn2.setIcon(icon)
        self.btn2.setIconSize(QtCore.QSize(200, 100))
        self.btn2.setObjectName("btn2")
        self.btn3 = QtWidgets.QPushButton(self.centralwidget)
        self.btn3.setGeometry(QtCore.QRect(60, 220, 221, 71))
        self.btn3.setText("")
        self.btn3.setIcon(icon)
        self.btn3.setIconSize(QtCore.QSize(200, 100))
        self.btn3.setObjectName("btn3")
        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(360, 20, 161, 81))
        self.title.setText("")
        self.title.setPixmap(QtGui.QPixmap(":/title/title.png"))
        self.title.setScaledContents(True)
        self.title.setObjectName("title")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    testWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(testWindow)
    ui.setupUi(testWindow)
    testWindow.show()
    sys.exit(app.exec_())