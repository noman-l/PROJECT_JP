import serial
from sendkakao import send_kakao_message


lat = 10.0  # 위도
lon = 10.0  # 경도

while True:
    command = input("명령어를 입력하세요 (go: 메시지 전송): ")
    if command.strip().lower() == "go":
        response = send_kakao_message(lat, lon)

        if response is None:
            print("메시지 전송 실패.")
        else:
            print("메시지가 성공적으로 전송되었습니다.")
