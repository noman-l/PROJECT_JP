import requests

def get_new_tokens(auth_code):
    response = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": "23996064e9c4fc796c5d57476a9318de",  # REST API 키
            "redirect_uri": "http://127.0.0.1:5000/oauth",  # 리다이렉트 URI
            "code": "59cBXf7TLJm46atJbWfbjVjr1FCmZxYO2zDLeoj-89zwJMCmoBfKBAAAAAQKPCSZAAABk0ML94Kt1856Xp2T3g"
  # 추출한 인증 코드
        },
    )

    if response.status_code != 200:
        print("토큰 발급 오류:", response.json())
        return None

    tokens = response.json()
    print("새로운 액세스 토큰:", tokens['access_token'])
    print("새로운 리프레시 토큰:", tokens['refresh_token'])
    return tokens

# 인증 코드 사용
auth_code = "59cBXf7TLJm46atJbWfbjVjr1FCmZxYO2zDLeoj-89zwJMCmoBfKBAAAAAQKPCSZAAABk0ML94Kt1856Xp2T3g"
tokens = get_new_tokens(auth_code)

if tokens:
    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']
    print("액세스 토큰:", access_token)
    print("리프레시 토큰:", refresh_token)
