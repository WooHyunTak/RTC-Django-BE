from datetime import datetime, timedelta
import logging
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)


class Token:
    def generate_token(self, user):
        try:
            if not user:
                raise ValueError("user_id is required")

            refresh = RefreshToken.for_user(user)
            return {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
            }
        except Exception as e:
            logger.error(f"Token 생성 오류: {e}")
            raise e
