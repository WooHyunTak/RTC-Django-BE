from common.utils.tokens import Token
from types import SimpleNamespace


class CookieJWTAuthentication(Token):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.rstrip("/")
        if path in ("/api/users/login", "/api/users/signup", "/api/users/refresh"):
            pass
        else:
            self.authenticate(request)
        return self.get_response(request)

    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")
        if not raw_token:
            return None
        payload_dict = self.verify_token(raw_token)
        if not payload_dict:
            return None
        payload = SimpleNamespace(**payload_dict)
        request.token_user = payload
        return payload
