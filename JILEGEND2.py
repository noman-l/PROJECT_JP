# -*- coding: utf-8 -*-
from PyQt5.QtCore import QCoreApplication, QDate, QTime, QTimer, QUrl, Qt, QSize, QThread, pyqtSignal, QRect
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QStackedWidget, QStatusBar, QWidget, QLineEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView
import serial
import speech_recognition as sr
import subprocess
import sys
import sendkakao_ver_3
import phonecall
import threading
import http.server
import socketserver
from flask import Flask, jsonify
from flask_cors import CORS
import time
import os

# Mock 처리 시작
try:
    import RPi.GPIO as GPIO
except ImportError:
    class GPIO:
        BCM = "BCM"
        OUT = "OUT"
        IN = "IN"
        HIGH = 1
        LOW = 0
        PUD_UP = "PUD_UP"  # Pull-Up 설정 추가
        PUD_DOWN = "PUD_DOWN"  # Pull-Down 설정 추가 (필요하면)

        @staticmethod
        def setmode(mode):
            print(f"GPIO Mode Set: {mode}")

        @staticmethod
        def setwarnings(flag):
            print(f"GPIO Warnings Set: {flag}")

        @staticmethod
        def setup(pin, mode, pull_up_down=None):
            print(f"GPIO Pin Setup: {pin}, Mode: {mode}, Pull: {pull_up_down}")

        @staticmethod
        def output(pin, state):
            print(f"GPIO Pin {pin} Output: {'HIGH' if state else 'LOW'}")

        @staticmethod
        def input(pin):
            print(f"GPIO Pin {pin} Read")
            return GPIO.HIGH  # Always return HIGH for simulation

        @staticmethod
        def PWM(pin, frequency):
            class MockPWM:
                def __init__(self, pin, frequency):
                    self.pin = pin
                    self.frequency = frequency

                def start(self, duty_cycle):
                    print(f"PWM Start: Pin {self.pin}, Frequency {self.frequency}, Duty Cycle {duty_cycle}")

                def ChangeDutyCycle(self, duty_cycle):
                    print(f"PWM Change Duty Cycle: Pin {self.pin}, Duty Cycle {duty_cycle}")

                def stop(self):
                    print(f"PWM Stop: Pin {self.pin}")

            return MockPWM(pin, frequency)

        @staticmethod
        def cleanup():
            print("GPIO Cleanup")

try:
    import spidev
except ImportError:
    class spidev:
        class SpiDev:
            def open(self, bus, device):
                print(f"SPI Open: Bus {bus}, Device {device}")

            def xfer2(self, data):
                print(f"SPI Transfer: {data}")
                return [0] * len(data)  # Return mock data

            def close(self):
                print("SPI Close")
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class ActuatorController:
#수정된 코드

    def __init__(self):
        # BTS7960 핀 설정
        self.RPWM = 12  # 엑츄에이터 전진 핀
        self.LPWM = 13  # 엑츄에이터 후진 핀

        # 스위치 및 홀센서 핀 설정
        self.SWITCH_PIN_0 = 20  # 스위치 상태 "0"
        self.SWITCH_PIN_1 = 26  # 스위치 상태 "1" 또는 "2"
        self.HALL_SENSOR_PIN = 27  # 홀 센서 핀

        # GPIO 설정
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RPWM, GPIO.OUT)
        GPIO.setup(self.LPWM, GPIO.OUT)
        GPIO.setup(self.SWITCH_PIN_0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.SWITCH_PIN_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.HALL_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # 상태 변수
        self.switch_state = {"switch_0": GPIO.HIGH, "switch_1": GPIO.HIGH}
        self.hall_sensor_state = GPIO.HIGH
        self.running = True  # 쓰레드 실행 여부

    def stop_actuator(self):
        """액추에이터 정지"""
        GPIO.output(self.RPWM, GPIO.LOW)
        GPIO.output(self.LPWM, GPIO.LOW)

    def forward_actuator(self):
        """액추에이터 전진"""
        GPIO.output(self.RPWM, GPIO.HIGH)
        GPIO.output(self.LPWM, GPIO.LOW)

    def reverse_actuator(self):
        """액추에이터 후진"""
        GPIO.output(self.RPWM, GPIO.LOW)
        GPIO.output(self.LPWM, GPIO.HIGH)

    def read_inputs(self):
        """스위치와 홀 센서 상태 읽기"""
        self.switch_state["switch_0"] = GPIO.input(self.SWITCH_PIN_0)
        self.switch_state["switch_1"] = GPIO.input(self.SWITCH_PIN_1)
        self.hall_sensor_state = GPIO.input(self.HALL_SENSOR_PIN)

    def control_actuator(self):
        """액추에이터 제어 로직"""
        if self.switch_state["switch_1"] == GPIO.LOW:  # 스위치 상태 "2"인 경우
            print("스위치 상태: 2 (전진)")
            self.forward_actuator()
        elif self.switch_state["switch_0"] == GPIO.LOW:  # 스위치 상태 "0"인 경우
            if self.hall_sensor_state == GPIO.LOW:  # 홀센서 자성 감지
                print("스위치 상태: 0 (자성 감지, 전진)")
                self.forward_actuator()
            else:  # 자성 없음
                print("스위치 상태: 0 (자성 없음, 후진)")
                self.reverse_actuator()
        else:  # 스위치 상태 "1"인 경우
            print("스위치 상태: 1 (후진)")
            self.reverse_actuator()

    def monitor_sensors(self):
        """스위치 및 홀 센서 상태를 지속적으로 모니터링"""
        try:
            print("스위치 및 홀센서 상태 모니터링 시작...")
            while self.running:
                self.read_inputs()
                print(f"스위치 상태 0: {'ON' if self.switch_state['switch_0'] == GPIO.LOW else 'OFF'}")
                print(f"스위치 상태 1: {'ON' if self.switch_state['switch_1'] == GPIO.LOW else 'OFF'}")
                print(f"홀센서 상태: {'자성 감지' if self.hall_sensor_state == GPIO.LOW else '자성 없음'}")
                print("-" * 30)
                time.sleep(0.5)  # 500ms 대기
        except KeyboardInterrupt:
            print("모니터링 중단")
        finally:
            GPIO.cleanup()

    def actuator_loop(self):
        """액추에이터 제어 쓰레드"""
        while self.running:
            self.read_inputs()
            self.control_actuator()
            time.sleep(0.1)  # 100ms 대기

    def start(self):
        """쓰레드 시작"""
        self.thread = threading.Thread(target=self.actuator_loop)
        self.thread.start()

    def stop(self):
        """쓰레드 종료"""
        self.running = False
        self.thread.join()
        self.stop_actuator()
        GPIO.cleanup()


'''class HX711Worker(QThread):
    weight_signal = pyqtSignal(float, float)  # 센서 A와 B의 무게를 전달하는 신호

    def __init__(self, dout_pin, pd_sck_pin, ref_unit_A=2100, ref_unit_B=120):
        super().__init__()
        self.hx711 = HX711(dout_pin, pd_sck_pin)
        self.hx711.set_reading_format("MSB", "MSB")
        self.hx711.reset()
        self.channel_A_gain = 128
        self.channel_B_gain = 32
        self.hx711.set_gain(self.channel_A_gain)
        self.ref_unit_A = ref_unit_A
        self.ref_unit_B = ref_unit_B
        self.running = True
        self.tare_all()

    def tare(self, channel='A'):
        if channel == 'A':
            self.hx711.set_gain(self.channel_A_gain)
        elif channel == 'B':
            self.hx711.set_gain(self.channel_B_gain)
        else:
            raise ValueError("Choose A or B")
        self.hx711.tare()

    def tare_all(self):
        self.tare(channel='A')
        self.tare(channel='B')

    def get_weight(self, channel='A', times=5):
        if channel == 'A':
            self.hx711.set_gain(self.channel_A_gain)
            self.hx711.set_reference_unit(self.ref_unit_A)
        elif channel == 'B':
            self.hx711.set_gain(self.channel_B_gain)
            self.hx711.set_reference_unit(self.ref_unit_B)
        else:
            raise ValueError("Choose A or B")
        return self.hx711.get_weight(times)

    def run(self):
        while self.running:
            try:
                weight_A = self.get_weight(channel='A')
                weight_B = self.get_weight(channel='B')
                self.weight_signal.emit(weight_A, weight_B)
                
                time.sleep(0.1)  # 0.1초 간격으로 데이터 갱신
            except Exception as e:
                print(f"HX711 스레드 오류: {e}")

    def stop(self):
        self.running = False
        self.hx711.power_down()
'''
R_PWM_B = 23
L_PWM_B = 24
R_PWM_F = 19
L_PWM_F = 16

GPIO.setup(R_PWM_B, GPIO.OUT)
GPIO.setup(L_PWM_B, GPIO.OUT)
GPIO.setup(R_PWM_F, GPIO.OUT)
GPIO.setup(L_PWM_F, GPIO.OUT)

pwm_r = GPIO.PWM(R_PWM_B, 50)
pwm_l = GPIO.PWM(L_PWM_B, 50)
pwm_r_F = GPIO.PWM(R_PWM_F, 50)
pwm_l_F = GPIO.PWM(L_PWM_F, 50)
pwm_r.start(0)
pwm_l.start(0)
pwm_r_F.start(0)
pwm_l_F.start(0)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def read_adc(channel):
    if channel < 0 or channel > 7:
        raise ValueError("채널 번호는 0부터 7사이 입니다.")
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

def control_motor(speed):
    if speed > 0: #forward direction
        pwm_r.ChangeDutyCycle(min(speed, 100))
        pwm_l.ChangeDutyCycle(0)
    elif speed < 0: #reverse direction
        pwm_r.ChangeDutyCycle(0)
        pwm_l.ChangeDutyCycle(min(abs(speed), 100))
    else: # stop
        pwm_r.ChangeDutyCycle(0)
        pwm_l.ChangeDutyCycle(0)

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
app = Flask(__name__)
CORS(app)
@app.route('/location')
def location():
    gpsLat, gpsLng = get_gps_data()
    return jsonify({"latitude": gpsLat, "longitude": gpsLng})


def run_flask_app():
    app.run(host="0.0.0.0", port=8001)

def initialize_label(label, text, font_size, background_color="#B4B6B8"):
        label.setText(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"""
            background-color: {background_color};
            font-size: {font_size}px;
            font-weight: bold;
        """)

class Ui_MainWindow(QMainWindow):
    image_path = r"C:\Users\pjo77\PycharmProjects\pythonProject1\HIHIHI\speed.png"

    def __init__(self):
        self.gpsLat = 37.6303483
        self.gpsLng = 126.8335345
        super().__init__()
        self.setObjectName("MainWindow")
        self.resize(1024, 600)
        self.setMinimumSize(QSize(1024, 600))
        self.setMaximumSize(QSize(1024, 600))
        # self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Initialize UI components
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.initUI()
        self.retranslateUi(self)

        # Set up GPS worker
        self.gps_worker = GPSWorker('/dev/ttyAMA0')
        self.gps_worker.gps_signal.connect(self.update_gps)
        self.gps_worker.start()

        self.speed_1_timer = QTimer()
        self.speed_1_timer.timeout.connect(self.update_motor_speed_1)

        self.speed_2_timer = QTimer()
        self.speed_2_timer.timeout.connect(self.update_motor_speed_2)

        self.speed_3_timer = QTimer()
        self.speed_3_timer.timeout.connect(self.update_motor_speed_3)

        self.speed_4_timer = QTimer()
        self.speed_4_timer.timeout.connect(self.update_motor_speed_front)
        self.motor_running = False

        self.speed_5_timer = QTimer()
        self.speed_5_timer.timeout.connect(self.joystick_motor_control)
        self.joystick_mode = False

        # Timer for updating time display
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)  # Update every second


        
        '''self.hx711_worker = HX711Worker(5,6)
        self.hx711_worker.weight_signal.connect(self.update_weight_labels)
        self.hx711_worker.start()'''

    def initUI(self):
        # Set up stacked widget for different pages
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(0, 10, 1024, 600)

        # Main page setup
        self.page = QWidget()

        # Google Maps widget on main page
        from PyQt5.QtWebEngineWidgets import QWebEngineView  # QWebView 대신

        # Google Maps widget on main page
        self.page.setObjectName("page")
        self.webView = QWebEngineView(self.page)  # QWebEngineView로 대체
        self.webView.setGeometry(310, 90, 691, 471)
        self.webView.setUrl(QUrl('http://localhost:8000/map.html'))

        # Clock label
        self.label = QLabel(self.page)
        self.label.setGeometry(660, 0, 360, 50)
        font = QFont()
        self.label.setStyleSheet("font-size: 25px; font-weight: bold;")
        self.label.setFont(font)

        # mic label
        self.miclabel = QLabel(self.page)
        self.miclabel.setGeometry(660, 35, 360, 50)
        self.miclabel.setStyleSheet("font-size: 25px; font-weight: bold;")
        self.miclabel.setFont(font)

        # GPS status label
        self.label_gps = QLabel(self.page)
        self.label_gps.setGeometry(10, 420, 300, 50)
        self.label_gps.setFont(font)

        # Buttons on page
        self.pushButton_5 = QPushButton(self.page)
        self.pushButton_5.setGeometry(40, 90, 230, 110)
        self.pushButton_5.setStyleSheet("background-image: url('emrcall.png'); background-position: center;")
        self.pushButton_5.clicked.connect(self.go_to_page_4)

        self.pushButton_4 = QPushButton(self.page)
        self.pushButton_4.setGeometry(40, 210, 230, 110)
        self.pushButton_4.setStyleSheet("background-image: url('loc.png'); background-position: center;")
        self.pushButton_4.clicked.connect(self.send_kakao_message)

        self.pushButton_6 = QPushButton(self.page)
        self.pushButton_6.setGeometry(40, 330, 230, 110)
        self.pushButton_6.setStyleSheet("background-image: url('speed.png'); background-position: center;")
        self.pushButton_6.clicked.connect(self.go_to_page_2)

        self.justlabel_1 = QLabel("현재 모드", self.page)
        self.justlabel_1.setGeometry(340, 0, 90, 40)
        self.justlabel_1.setStyleSheet('font-size: 20px')

        self.statelabel_1 = QLabel("초기상태", self.page)
        self.statelabel_1.setGeometry(340, 33, 200, 50)
        self.statelabel_1.setAlignment(Qt.AlignCenter)
        self.statelabel_1.setStyleSheet("""
            background-color: #B4B6B8;
            font-size: 30px;
            font-weight: bold;
        """)

        # Title label
        # ROOKIE
        self.label_2 = QLabel(self.page)
        self.label_2.setGeometry(40, 13, 230, 67)
        self.label_2.setStyleSheet("background-image: url('rookie1.png'); background-position: center;")

        # 압력 표시 라벨
        self.label_5 = QLabel(self.page)
        self.label_5.setObjectName("weight")
        self.label_5.setGeometry(QRect(270,50,361,31))

        self.label_6 = QLabel(self.page)
        self.label_6.setObjectName("weight_2")
        self.label_6.setGeometry(QRect(270,70,361,31))

        # Settings button
        self.set = QLabel(self.page)
        self.set.setGeometry(960, 0, 50, 50)
        self.set.setStyleSheet("background-image: url('setting.png');")
        self.set.mousePressEvent = (self.go_to_page_3)

        self.pushButton_speech = QPushButton(self.page)
        self.pushButton_speech.setGeometry(40, 450, 230, 110)
        self.pushButton_speech.setStyleSheet("background-image: url('mic.png'); background-position: center;")
        self.pushButton_speech.clicked.connect(self.recognize_speech)
        self.stackedWidget.addWidget(self.page)

        # Page 2 setup 속도
        self.page_2 = QWidget()
        font1 = QFont()
        font1.setPointSize(20)
        
        self.pushButton = QPushButton(self.page_2)
        self.pushButton.setGeometry(20, 40, 650, 96)
        self.pushButton.setStyleSheet("background-image: url('state.png'); background-position: center;")
        self.pushButton.clicked.connect(self.speed_0_status)

        self.pushButton_2 = QPushButton(self.page_2)
        self.pushButton_2.setGeometry(20, 146, 650, 96)
        self.pushButton_2.setStyleSheet("background-image: url('speedlv1.png'); background-position: center;")
        self.pushButton_2.clicked.connect(self.speed_1_status)

        self.pushButton_3 = QPushButton(self.page_2)
        self.pushButton_3.setGeometry(20, 252, 650, 96)
        self.pushButton_3.setStyleSheet("background-image: url('speedlv2.png'); background-position: center;")
        self.pushButton_3.clicked.connect(self.speed_2_status)

        self.pushButton_7 = QPushButton(self.page_2)
        self.pushButton_7.setGeometry(20, 464, 650, 96)
        self.pushButton_7.setStyleSheet("background-image: url('free.png'); background-position: center;")
        self.pushButton_7.clicked.connect(self.speed_3_status)

        self.pushButton_14 = QPushButton(self.page_2)
        self.pushButton_14.setGeometry(20, 358, 650, 96)
        self.pushButton_14.setStyleSheet("background-image: url('joy.png'); background-position: center;")
        self.pushButton_14.clicked.connect(self.toggle_joystick_mode)

        self.backButton_1 = QPushButton(self.page_2)
        self.backButton_1.setGeometry(824, 500, 150, 50)
        self.backButton_1.setStyleSheet("background-image: url('backbutton.png'); background-position: center;")
        self.backButton_1.clicked.connect(self.go_to_page)

        self.justlabel_2 = QLabel("현재 모드", self.page_2)
        self.justlabel_2.setGeometry(780, 158, 130, 70)
        self.justlabel_2.setStyleSheet('font-size: 30px')

        self.statelabel_2 = QLabel("초기상태", self.page_2)
        self.statelabel_2.setGeometry(720, 220, 250, 110)
        self.statelabel_2.setAlignment(Qt.AlignCenter)
        self.statelabel_2.setStyleSheet("""
            background-color: #B4B6B8;
            font-size: 45px;
            font-weight: bold;
        """)

        self.stackedWidget.addWidget(self.page_2)

        # Page 3 setup 설정
        self.page_3 = QWidget()
        font2 = QFont()
        font2.setPointSize(16)

        self.rookie = QLabel(self.page_3)
        self.rookie.setGeometry(50, 50, 500, 500)
        self.rookie.setStyleSheet("background-image: url('rookie.png');")

        self.swver = QLabel(self.page_3)
        self.swver.setGeometry(630, 50, 190, 50)
        self.swver.setFont(font2)

        self.reboot = QPushButton(self.page_3)
        self.reboot.setGeometry(630, 130, 150, 50)
        self.reboot.setStyleSheet("background-image: url('reboot.png'); background-position: center;")
        self.reboot.clicked.connect(self.reboot_program)

        self.noti = QPushButton(self.page_3)
        self.noti.setGeometry(630, 210, 150, 50)
        self.noti.setStyleSheet("background-image: url('noti.png'); background-position: center;")
        #self.noti.clicked.connect(self.)

        self.phoneconnection = QPushButton(self.page_3)
        self.phoneconnection.setGeometry(630, 290, 150, 50)
        self.phoneconnection.setStyleSheet("background-image: url('phoneconnection.png'); background-position: center;")
        self.phoneconnection.clicked.connect(self.connect_adb)

        self.shutdown = QPushButton(self.page_3)
        self.shutdown.setGeometry(630, 370, 150, 50)
        self.shutdown.setStyleSheet("background-image: url('off.png'); background-position: center;")
        self.shutdown.clicked.connect(self.shutdownpower)

        self.backButton_2 = QPushButton(self.page_3)
        self.backButton_2.setGeometry(824, 500, 150, 50)
        self.backButton_2.setStyleSheet("background-image: url('backbutton.png'); background-position: center;")
        self.backButton_2.clicked.connect(self.go_to_page)

        self.stackedWidget.addWidget(self.page_3)


        # Page 4
        self.page_4 = QWidget()
        self.backButton_3 = QPushButton(self.page_4)
        self.backButton_3.setGeometry(824, 500, 150, 50)
        self.backButton_3.setStyleSheet("background-image: url('backbutton.png'); background-position: center;")
        self.backButton_3.clicked.connect(self.go_to_page)

        self.pushButton_10 = QPushButton(self.page_4)
        self.pushButton_10.setGeometry(140, 70, 250, 80)
        self.pushButton_10.setStyleSheet("background-image: url('112.png'); background-position: center;")
        self.pushButton_10.clicked.connect(self.call_112)

        self.pushButton_11 = QPushButton(self.page_4)
        self.pushButton_11.setGeometry(140, 180, 250, 80)
        self.pushButton_11.setStyleSheet("background-image: url('119.png'); background-position: center;")
        self.pushButton_11.clicked.connect(self.call_119)

        self.pushButton_12 = QPushButton(self.page_4)
        self.pushButton_12.setGeometry(140, 290, 250, 80)
        self.pushButton_12.setStyleSheet("background-image: url('nok1.png'); background-position: center;")
        self.pushButton_12.clicked.connect(self.call_nok)

        self.pushButton_13 = QPushButton(self.page_4)
        self.pushButton_13.setGeometry(140, 400, 250, 80)
        self.pushButton_13.setStyleSheet("background-image: url('nok2.png'); background-position: center;")
        self.pushButton_13.clicked.connect(self.call_nok)

        self.callButton = QPushButton(self.page_4)
        self.callButton.setGeometry(600, 364, 70, 70)
        self.callButton.setStyleSheet("background-image: url('call.png'); background-position: center;")
        self.callButton.clicked.connect(self.call_dialpad)

        self.hangupButton = QPushButton(self.page_4)
        self.hangupButton.setGeometry(760, 364, 70, 70)
        self.hangupButton.setStyleSheet("background-image: url('hangup.png'); background-position: center;")        
        self.hangupButton.clicked.connect(self.hang_up)

        self.dialpad = QLineEdit(self.page_4)
        self.dialpad.setGeometry(600, 62, 190, 40)
        self.dialpad.setAlignment(Qt.AlignRight)
        self.dialpad.setFont(QFont("Arial", 18))

        self.clearbutton = QPushButton("←", self.page_4)
        self.clearbutton.setGeometry(800, 62, 40, 40)
        self.clearbutton.clicked.connect(self.clear_last_digit)

        button_size = 70
        button_spacing = 10
        start_x, start_y = 600, 124

        dial_buttons = [
            '1', '2', '3',
            '4', '5', '6',
            '7', '8', '9',
            '', '0', ''
        ]

        font2 = QFont()
        font2.setPointSize(24)

        for i, text in enumerate(dial_buttons):
            if not text:
                continue
            row = i // 3
            col = i % 3
            x = start_x + col * (button_size + button_spacing)
            y = start_y + row * (button_size + button_spacing)

            button = QPushButton(text, self.page_4)
            button.setFont(font2)
            button.setGeometry(QRect(x, y, button_size, button_size))
            button.clicked.connect(lambda checked, num=text: self.append_to_input(num))


        self.stackedWidget.addWidget(self.page_4)

        # Status bar
        self.setStatusBar(QStatusBar(self))


    def update_gps(self, lat, lng):
        # Update instance variables with new GPS data
        self.gpsLat = lat
        self.gpsLng = lng
        self.label_gps.setText(f"위도 {lat}, 경도 {lng}")
        print(f"Updated GPS coordinates: 위도 {self.gpsLat}, 경도 {self.gpsLng}")
    def update_weight_labels(self,weight_A,weight_B):

        self.label_5.setText(f"weight A : {weight_A:.2f}g")
        self.label_6.setText(f"weight B : {weight_B:.2f}g")
    def closeEvent(self,event):
        self.hx711_worker.stop()
        self.hx711_worker.wait()
        super().closeEvent(event)
    def update_clock(self):
        current_date = QDate.currentDate().toString('yyyy-MM-dd (ddd)')
        current_time = QTime.currentTime().toString('HH:mm:ss')
        self.label.setText(f"{current_date} {current_time}")

    def go_to_page(self):
        self.stackedWidget.setCurrentIndex(0)

    def go_to_page_2(self):
        self.stackedWidget.setCurrentIndex(1)

    def go_to_page_3(self, event):
        self.stackedWidget.setCurrentIndex(2)

    def go_to_page_4(self):
        self.stackedWidget.setCurrentIndex(3)



    def send_kakao_message(self):
        print(f"전송할 GPS 데이터: 위도 {self.gpsLat}, 경도 {self.gpsLng}")

        # 절대 경로 설정
        map_file_path = '/home/rookie/Desktop/ver_10_09/map.html'

        try:
            # 기존 HTML 파일 열기
            with open(map_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            # GPS 데이터를 반영하여 HTML 수정
            updated_html = html_content.replace(
                'updateMapPosition(37.3595704, 127.105399);',
                f'updateMapPosition({self.gpsLat}, {self.gpsLng});'
            )

            # 수정된 내용을 다시 HTML 파일에 쓰기
            with open(map_file_path, 'w', encoding='utf-8') as file:
                file.write(updated_html)

            print("HTML 파일에 위치 업데이트 완료.")

        except FileNotFoundError:
            print("HTML 파일을 찾을 수 없습니다. 경로를 확인하세요.")
        except Exception as e:
            print(f"HTML 업데이트 중 오류 발생: {e}")

        # 카카오 메시지 전송
        sendkakao_ver_3.send_kakao_message(
            "MvVF9937EBBxh7YZt6z8a4WGwZfQsgZiAAAAAgo9c-wAAAGTQw5Hi8TTXs9KIG_V",
            self.gpsLat,
            self.gpsLng
        )

    def recognize_speech(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            print("Listening...")
            self.pushButton_speech.setStyleSheet("background-image: url('listen.png'); background-position: center;")
            QApplication.processEvents()
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            recognized_text = recognizer.recognize_google(audio, language="ko-KR")
            print(f"Recognized Speech: {recognized_text}")
            self.miclabel.setText(recognized_text)
            QTimer.singleShot(3000, lambda: self.miclabel.setText(""))
            if recognized_text == "초기상태" or recognized_text == "정지":
                initialize_label(self.statelabel_1, "초기상태", 30, background_color="#B4B6B8")
                initialize_label(self.statelabel_2, "초기상태", 45, background_color="#B4B6B8")
                self.speed_0_status()
            elif recognized_text == "1단계":
                initialize_label(self.statelabel_1, "속도 : 1단계", 30, background_color="#6DC9FF")
                initialize_label(self.statelabel_2, "속도 : 1단계", 45, background_color="#6DC9FF")
                self.speed_1_status()
            elif recognized_text == "2단계":
                initialize_label(self.statelabel_1, "속도 : 2단계", 30, background_color="#5271FF")
                initialize_label(self.statelabel_2, "속도 : 2단계", 45, background_color="#5271FF")
                self.speed_2_status()
            elif recognized_text == "조이스틱 모드" or recognized_text == "조이스틱":
                initialize_label(self.statelabel_1, "조이스틱 모드", 25, background_color="#FF5757")
                initialize_label(self.statelabel_2, "조이스틱 모드", 40, background_color="#FF5757")
                self.toggle_joystick_mode()
            elif recognized_text == "자유 모드" or recognized_text == "자유":
                initialize_label(self.statelabel_1, "자유 모드", 30, background_color="#FFDE5A")
                initialize_label(self.statelabel_2, "자유 모드", 45, background_color="#FFDE5A")
                self.speed_3_status()

        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        self.pushButton_speech.setStyleSheet("background-image: url('mic.png'); background-position: center;")
        QApplication.processEvents()
    def stop_motor(self):
        pwm_r.stop()
        pwm_l.stop()
        pwm_r_F.stop()
        pwm_l_F.stop()

    def reboot_program(self):
        self.stop_motor()
        GPIO.cleanup()
        time.sleep(1)
        python = sys.executable
        subprocess.Popen([python] + sys.argv)
        QCoreApplication.quit()
    
    def shutdownpower(self):
        app_instance = QCoreApplication.instance()
        if app_instance is not None:
            print("Application shutting down...")
            try:
                GPIO.cleanup()
                app_instance.quit()
                os.system("sudo shutdown -h now")
            except Exception as e:
                print(f"Error during application shutdown: {e}")
        else:
            print("No QCoreApplication instance found!")


    def call_112(self):
        phonecall.call_112(self)

    def call_119(self):
        phonecall.call_119(self)

    def call_nok(self):
        phonecall.call_nok(self)
    
    def call_dialpad(self):
        phonecall.call_dialpad(self)

    def hang_up(self):
        phonecall.hang_up(self)
    
    def make_call(self, phone_number):
        phonecall.make_call(self, phone_number)

    def connect_adb(self):
        phonecall.connect_adb(self)

    def clear_last_digit(self):
        current_text = self.dialpad.text()
        self.dialpad.setText(current_text[:-1])

    def append_to_input(self, num):
        current_text = self.dialpad.text()
        self.dialpad.setText(current_text + num)

    def toggle_joystick_mode(self):
        self.speed_5_timer.start(100)
        self.pushButton_14.clicked.connect(self.go_to_page)
        initialize_label(self.statelabel_1, "조이스틱 모드", 25, background_color="#FF5757")
        initialize_label(self.statelabel_2, "조이스틱 모드", 40, background_color="#FF5757")

    def joystick_motor_control(self):
        y_value = read_adc(1)

        y_offset = y_value - 512
        if abs(y_offset) < 50:
            motor_speed = 0
        else:
            motor_speed = int((y_offset / 512) * 100)

        control_motor(motor_speed)
        print(f"Joystick Y: {y_value}, Motor Speed: {motor_speed}")

    def stop_all_timers(self):
        self.speed_1_timer.stop()
        self.speed_2_timer.stop()
        self.speed_3_timer.stop()
        self.speed_4_timer.stop()
        self.speed_5_timer.stop()

    def start_speed_timer(self, speed):
        if speed == 1:
            self.update_motor_speed_1()
            self.speed_1_timer.start(100)
        elif speed == 2:
            self.update_motor_speed_2()
            self.speed_2_timer.start(100)
        elif speed == 3:
            self.update_motor_speed_3()
            self.speed_3_timer.start(100)

    # 초기상태 click
    def speed_0_status(self):
        self.stop_all_timers()
        self.pushButton.clicked.connect(self.go_to_page)
        initialize_label(self.statelabel_1, "초기상태", 30, background_color="#B4B6B8")
        initialize_label(self.statelabel_2, "초기상태", 45, background_color="#B4B6B8")

    # 속도 : 1단계 click
    def speed_1_status(self):
        self.stop_all_timers()
        self.start_speed_timer(1)
        self.pushButton_2.clicked.connect(self.go_to_page)
        initialize_label(self.statelabel_1, "속도 : 1단계", 30, background_color="#6DC9FF")
        initialize_label(self.statelabel_2, "속도 : 1단계", 45, background_color="#6DC9FF")

    def update_motor_speed_1(self):
        pwm_r.ChangeDutyCycle(25)
        pwm_l.ChangeDutyCycle(0)

    # 속도 : 2단계 click
    def speed_2_status(self):
        self.stop_all_timers()
        self.start_speed_timer(2)
        self.pushButton_3.clicked.connect(self.go_to_page)
        initialize_label(self.statelabel_1, "속도 : 2단계", 30, background_color="#5271FF")
        initialize_label(self.statelabel_2, "속도 : 2단계", 45, background_color="#5271FF")

    def update_motor_speed_2(self):
        pwm_l.ChangeDutyCycle(25)
        time.sleep(0.1)
        pwm_l.ChangeDutyCycle(40)

    # 자유 모드 click
    def speed_3_status(self):
        self.stop_all_timers()
        self.start_speed_timer(3)
        self.pushButton_7.clicked.connect(self.go_to_page)
        initialize_label(self.statelabel_1, "자유 모드", 30, background_color="#FFDE5A")
        initialize_label(self.statelabel_2, "자유 모드", 45, background_color="#FFDE5A")


    def update_motor_speed_3(self):
        try:
            max_pressure = 1000
            pressure_value_1 = self.val_1
            pressure_value_2 = self.val_2
            average_pressure = (pressure_value_1 + pressure_value_2) / 2
            if pressure_value_1 <= 0 or pressure_value_2 <= 0:
                duty_cycle = 0
            elif average_pressure <= 0:
                duty_cycle = 0
            elif average_pressure >= max_pressure:
                duty_cycle = 100
            else:
                duty_cycle = (average_pressure / max_pressure) * 100 
            pwm_back.ChangeDutyCycle(duty_cycle)
        except Exception as e:
            print(f"Error: {e}")

    def update_motor_speed_front(self):
        try:
            pressure_value_1 = self.val_1
            pressure_value_2 = self.val_2
            if pressure_value_1 < pressure_value_2 and not self.motor_running:
                self.motor_running = True
                duty_cycle = 60
                pwm_l_F.ChangeDutyCycle(duty_cycle)
                pwm_r_F.ChangeDutyCycle(0)
                self.motor_timer_left = QTimer(self)
                self.motor_timer_left.setSingleShot(True)
                self.motor_timer_left.start(2000)
                self.motor_timer_left.timeout.connect(self.stop_motor_front)
                
            else:
                self.motor_running = True
                duty_cycle = 60
                pwm_r_F.ChangeDutyCycle(duty_cycle)
                pwm_l_F.ChangeDutyCycle(0)
                self.motor_timer_right = QTimer(self)
                self.motor_timer_right.setSingleShot(True)
                self.motor_timer_right.start(2000)
                self.motor_timer_right.timeout.connect(self.stop_motor_front)
                
                
        except Exception as e:
            print(f"Error in update_motor_speed_front: {e}")

    def stop_motor_front(self):
        pwm_r_F.ChangeDutyCycle(0)
        pwm_l_F.ChangeDutyCycle(0)
        self.motor_running = False

    # text
    def retranslateUi(self, MainWindow):
        self.swver.setText(QCoreApplication.translate("MainWindow", "S/W Version : 0.0.1", None))

def start_http_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8000), handler) as httpd:
        print("Serving HTTP on port 8000")
        httpd.serve_forever()

def get_gps_data():
    return window.gpsLat,window.gpsLng
if __name__ == "__main__":
    # HTTP 서버 및 Flask 애플리케이션 실행
    server_thread = threading.Thread(target=start_http_server)
    server_thread.daemon = True
    server_thread.start()

    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    # ActuatorController 실행
    actuator = ActuatorController()
    actuator.start()  # actuator_loop 실행

    # 필요한 경우 모니터링 활성화
    monitor_sensors_enabled = True  # True 시 센서 모니터링도 활성화
    if monitor_sensors_enabled:
        actuator_monitor_thread = threading.Thread(target=actuator.monitor_sensors)
        actuator_monitor_thread.daemon = True
        actuator_monitor_thread.start()

    try:
        # PyQt5 GUI 실행
        app = QApplication(sys.argv)
        window = Ui_MainWindow()
        window.show()
        sys.exit(app.exec_())

    except KeyboardInterrupt:
        print("프로그램 종료 요청됨...")

    finally:
        actuator.stop()
        if monitor_sensors_enabled:
            actuator.running = False  # monitor_sensors 루프 종료
