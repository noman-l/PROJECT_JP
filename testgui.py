import RPi.GPIO as GPIO
import time
import os

# PWM 핀 설정
R_PWM = 12
L_PWM = 13
count_file = "count.txt"

# GPIO 초기화
GPIO.setmode(GPIO.BCM)
GPIO.setup(R_PWM, GPIO.OUT)
GPIO.setup(L_PWM, GPIO.OUT)

pwm_r = GPIO.PWM(R_PWM, 50)  # 50Hz PWM
pwm_l = GPIO.PWM(L_PWM, 50)
pwm_r.start(0)
pwm_l.start(0)

# 카운트 파일 로드
def load_count():
    if os.path.exists(count_file):  # 파일이 존재하면
        with open(count_file, "r") as file:
            try:
                return int(file.read().strip())  # 숫자로 변환
            except ValueError:
                return 0  # 변환 실패 시 기본값 0 반환
    return 0  # 파일이 없으면 기본값 0 반환

# 카운트 값 저장
def save_count(count):
    with open(count_file, "w") as file:
        file.write(str(count))  # 값을 문자열로 저장

# 초기 카운트 값
count = load_count()
print(f"초기 카운트 값: {count}")

# 전진 함수
def forward():
    global count
    if count >= 3:
        print("카운트 초과! 전진 불가.")
        stop_motor()
        return
    print("전진 중...")
    pwm_r.ChangeDutyCycle(25)
    pwm_l.ChangeDutyCycle(0)
    time.sleep(2)
    stop_motor()
    count += 1
    save_count(count)

# 후진 함수
def back():
    global count
    if count <= -3:
        print("카운트 초과! 후진 불가.")
        stop_motor()
        return
    print("후진 중...")
    pwm_r.ChangeDutyCycle(0)
    pwm_l.ChangeDutyCycle(25)
    time.sleep(2)
    stop_motor()
    count -= 1
    save_count(count)

# 모터 정지 함수
def stop_motor():
    print("모터 정지")
    pwm_r.ChangeDutyCycle(0)
    pwm_l.ChangeDutyCycle(0)

# 동작 수행 함수
def execute_motor_action(L_hdl, R_hdl):
    if L_hdl > R_hdl and L_hdl - R_hdl > 100:
        back()
    elif R_hdl > L_hdl and R_hdl - L_hdl > 100:
        forward()
    else:
        print("동작 조건에 맞지 않습니다. 모터 정지.")
        stop_motor()

# 종료 처리
def cleanup():
    pwm_r.stop()
    pwm_l.stop()
    GPIO.cleanup()
