import requests
import json

def refresh_access_token(refresh_token):
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": "23996064e9c4fc796c5d57476a9318de",
        "refresh_token": refresh_token
    }

    response = requests.post(url, data=data)
    if response.status_code == 200:
        tokens = response.json()
        new_access_token = tokens['access_token']
        new_refresh_token = tokens['refresh_token']
        print("새로운 액세스 토큰:", new_access_token)
        print("새로운 리프레시 토큰:", new_refresh_token)
        return new_access_token, new_refresh_token
    else:
        print("토큰 재발급 오류:", response.json())
        return None, None

# 카카오톡 메시지를 전송하는 함수
def send_kakao_message(access_token):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",  # x-www-form-urlencoded로 설정합니다.
    }

    # 템플릿 오브젝트를 JSON 형식으로 정의합니다.
    template_object = {
        "object_type": "text",
        "text": "안녕하세요! 이것은 KakaoTalk 메시지입니다.",
        "link": {
            "web_url": "https://www.example.com",
            "mobile_web_url": "https://www.example.com"
        },
        "button_title": "웹사이트로 가기"
    }

    # JSON 데이터를 문자열로 변환
    template_object_json = json.dumps(template_object)

    data = {
        "template_object": template_object_json  # 문자열로 설정
    }

    # data 파라미터를 사용하여 데이터를 전송합니다.
    response = requests.post(url, headers=headers, data=data)

    # 응답 확인
    if response.status_code == 200:
        print("메시지가 성공적으로 전송되었습니다.")
        return response  # 응답 객체를 반환
    else:
        print("메시지 전송 오류:", response.json())
        return None  # 오류 시 None 반환

# 액세스 토큰 및 리프레시 토큰을 설정
access_token = "HCNPkwyX-rwdwISJd3n896tH25yuj93EAAAAAQo8IlEAAAGSmokpZcTTXs9KIG_V"
refresh_token = "UwZLmEB13Umqk3uFuz3g8CltdTpc5FsZAAAAAgo8IlEAAAGSmokpYMTTXs9KIG_V"  # 예시 리프레시 토큰

# 메시지를 전송하려고 시도
response = send_kakao_message(access_token)

# 만약 메시지 전송이 실패하면 리프레시 토큰으로 새 액세스 토큰을 요청
if response is None:  # 메시지 전송이 실패했을 때
    new_access_token, new_refresh_token = refresh_access_token(refresh_token)
    if new_access_token:
        send_kakao_message(new_access_token)
