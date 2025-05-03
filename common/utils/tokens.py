from datetime import datetime, timedelta
import logging
import jwt
from rtc_django_chat.settings import JWT_SECRET_KEY, JWT_ALGORITHM

logger = logging.getLogger(__name__)


class Token:
    SECRET_KEY = JWT_SECRET_KEY
    ALGORITHM = JWT_ALGORITHM

    def generate_token(self, user, token_type="access"):
        try:
            if not user:
                raise ValueError("user_id is required")

            if token_type == "access":
                token = jwt.encode(
                    {"id": user.id, "exp": datetime.now() + timedelta(days=1)},
                    self.SECRET_KEY,
                    algorithm=self.ALGORITHM,
                )
                return token
            elif token_type == "refresh":
                token = jwt.encode(
                    {"id": user.id, "exp": datetime.now() + timedelta(days=7)},
                    self.SECRET_KEY,
                    algorithm=self.ALGORITHM,
                )
                return token
        except Exception as e:
            logger.error(f"Token 생성 오류: {e}")
            raise e

    def verify_token(self, token):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except Exception as e:
            logger.error(f"Token 검증 오류: {e}")
            raise e

    def decode_token(self, token):
        try:
            return jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
        except Exception as e:
            logger.error(f"Token 디코딩 오류: {e}")
            raise e

    def set_token(self, user):
        access_token = self.generate_token(user)
        refresh_token = self.generate_token(user, "refresh")
        return {"access_token": access_token, "refresh_token": refresh_token}

    def set_cookie(self, response, token):
        response.set_cookie(
            key="access_token",
            value=token["access_token"],
            httponly=True,
            samesite="None",
            secure=True,
        )
        response.set_cookie(
            key="refresh_token",
            value=token["refresh_token"],
            httponly=True,
            samesite="None",
            secure=True,
        )
        return response
