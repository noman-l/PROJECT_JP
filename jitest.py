# -*- coding: utf-8 -*-
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("navermap")
        self.setGeometry(100, 100, 800, 480)
        self.webEngineView = QWebEngineView(self)
        self.setCentralWidget(self.webEngineView)

        self.webEngineView.setUrl(QUrl("http://localhost:8000/map.html"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
