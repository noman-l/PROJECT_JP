from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import os


class WebChannel(QObject):
    def __init__(self):
        super().__init__()

    def log_message(self, message):
        print(f"JavaScript log: {message}")


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Naver Map API Test")
        self.setGeometry(100, 100, 800, 600)

        self.webEngineView = QWebEngineView(self)
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "map.html"))
        self.webEngineView.setUrl(QUrl.fromLocalFile(file_path))

        self.setCentralWidget(self.webEngineView)


if __name__ == "__main__":
    client_id = "22wt5rtwpp"  # 여기에 NCP 콘솔의 클라이언트 ID를 입력하세요.

    app = QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec_())
