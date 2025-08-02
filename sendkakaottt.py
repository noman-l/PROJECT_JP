import json
import requests


def refresh_access_token(refresh_token):
    response = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "refresh_token",
            "client_id": "23996064e9c4fc796c5d57476a9318de",  # 클라이언트 ID
            "refresh_token": refresh_token
        },
    )

    if response.status_code != 200:
        print("토큰 재발급 오류:", response.json())
        # throw Exception 뭔가 해줘야함
        return

    tokens = response.json()
    new_access_token = tokens['access_token']
    new_refresh_token = tokens.get('refresh_token', None)  # nullable이라 이렇게 가져오는것으로 추정됨

    print("새로운 액세스 토큰:", new_access_token)
    if new_refresh_token:
        print("새로운 리프레시 토큰:", new_refresh_token)

    return new_access_token, new_refresh_token


def send_kakao_message(refresh_token, lat, lon):
    # 요청 보낼때마다 refresh
    access_token, refresh_token = refresh_access_token(refresh_token)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    template_object = {
        "object_type": "text",
        "text": f"현재 위치는 위도: {lat}, 경도: {lon}입니다.",
        "link": {
            "web_url": "https://www.example.com",
            "mobile_web_url": "https://www.example.com"
        },
        "button_title": "웹사이트로 가기"
    }

    template_object_json = json.dumps(template_object)
    data = {
        "template_object": template_object_json
    }

    response = requests.post(
        "https://kapi.kakao.com/v2/api/talk/memo/default/send",
        headers=headers,
        data=data,
    )

    # 실패하면 여기서 바로 떤짐
    if response.status_code != 200:
        print("메시지 전송 오류:", response.json())
        return None

    print("메시지가 성공적으로 전송되었습니다.")
    return response