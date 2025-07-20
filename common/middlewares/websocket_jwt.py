import urllib.parse
from types import SimpleNamespace

from common.utils.tokens import Token


class WebsocketJWTAuthentication(Token):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, scope, receive, send):
        is_authenticated = self.authenticate(scope)
        if not is_authenticated:
            # WebSocket 연결 거부
            async def close_websocket(receive, send):
                await send({"type": "websocket.close", "code": 4401})

            return close_websocket(receive, send)
        return self.get_response(scope, receive, send)

    def authenticate(self, scope):
        # headers에서 쿠키 정보 추출
        cookies = self.get_cookies_from_scope(scope)
        access_token = cookies.get("access_token")

        if not access_token:
            return False
        payload_dict = self.verify_token(access_token)
        if not payload_dict:
            return False
        payload = SimpleNamespace(**payload_dict)
        scope["token_user"] = payload
        return True

    def get_cookies_from_scope(self, scope):
        """
        scope의 headers에서 쿠키를 파싱하여 딕셔너리로 반환
        """
        cookies = {}
        for name, value in scope.get("headers", []):
            if name == b"cookie":
                cookie_header = value.decode("utf-8")
                # 쿠키 문자열 파싱
                for cookie in cookie_header.split(";"):
                    cookie = cookie.strip()
                    if "=" in cookie:
                        key, val = cookie.split("=", 1)
                        cookies[key.strip()] = urllib.parse.unquote(val.strip())
                break
        return cookies
