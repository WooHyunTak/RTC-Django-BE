from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        print("request.COOKIES", request.COOKIES)
        raw_token = request.COOKIES.get("access_token")
        if not raw_token:
            return None
        validated_token = self.get_validated_token(raw_token)
        print("validated_token", validated_token)
        return self.get_user(validated_token), validated_token
