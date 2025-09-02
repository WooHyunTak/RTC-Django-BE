import logging
from types import SimpleNamespace

from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils.tokens import Token
from user_channel.serializers import UserChannelSerializer

from .models import FriendStatus, UserFriend, UserMain, UserProfile
from .serializers import (
    UserFriendSerializer,
    UserMainCreateSerializer,
    UserMainSerializer,
)

logger = logging.getLogger(__name__)


class UserMainLoginView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = Token()

    def post(self, request):
        try:
            login_email = request.data.get("loginEmail")
            login_password = request.data.get("loginPassword")

            # 필수 파라미터 검사
            if not login_email or not login_password:
                return Response(
                    {"message": "이메일 또는 비밀번호가 입력되지 않았습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user_main = UserMain.objects.select_related("userprofile").get(
                email=login_email
            )
            serializer = UserMainSerializer(user_main)
            if user_main.password != login_password:
                return Response(
                    {"message": "비밀번호가 일치하지 않습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tokens = self.token.set_token(user_main)
            user_main.refresh_token = tokens["refresh_token"]
            user_main.save()
            success_response = Response(
                {
                    "message": "로그인 성공",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
            success_response = self.token.set_cookie(success_response, tokens)
            return success_response
        except Exception as e:
            logger.error(f"UserMainLoginView 오류: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = Token()

    def post(self, request):
        try:
            # 미들웨어에서 설정한 token_user가 있는지 확인
            if hasattr(request, "token_user"):
                user_main = UserMain.objects.select_related("userprofile").get(
                    id=request.token_user.id
                )
                user_main.refresh_token = None
                user_main.save()
                success_response = Response(
                    {"message": "로그아웃 성공"}, status=status.HTTP_200_OK
                )
                success_response = self.token.delete_cookie(success_response)
                return success_response
            else:
                # 미들웨어에서 token_user를 설정하지 못했을 경우 (토큰이 없거나 유효하지 않음)
                return Response(
                    {"message": "인증되지 않은 사용자입니다."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except Exception as e:
            logger.error(f"UserLogoutView 오류: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserGetMeView(APIView):
    def get(self, request):
        try:
            # 미들웨어에서 설정한 token_user가 있는지 확인
            if hasattr(request, "token_user"):
                user_main = UserMain.objects.select_related("userprofile").get(
                    id=request.token_user.id
                )
                serializer = UserMainSerializer(user_main)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # 미들웨어에서 token_user를 설정하지 못했을 경우 (토큰이 없거나 유효하지 않음)
                return Response(
                    {"message": "인증되지 않은 사용자입니다."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except Exception as e:
            logger.error(f"UserGetMeView 오류: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserSignUpView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = Token()

    def post(self, request):
        try:
            user_data = {
                "name": request.data.get("name"),
                "password": request.data.get("loginPassword"),
                "email": request.data.get("loginEmail"),
            }
            # 트렌젝션 시작 #
            with transaction.atomic():
                # 유저 유효성 검사
                serializer = UserMainCreateSerializer(
                    data=user_data,
                )
                if serializer.is_valid(raise_exception=True):
                    # 유저 생성
                    user_main = serializer.save()
                    # 유저 프로필 생성
                    if request.data.get("imageUrl", None):
                        UserProfile.objects.create(
                            user=user_main,
                            image_url=request.data.get("imageUrl", None),
                        )
                    data = serializer.data
                    data.pop("password", None)
                    success_response = Response(
                        {"message": "회원가입 성공", "data": data},
                        status=status.HTTP_201_CREATED,
                    )
                    tokens = self.token.set_token(user_main)
                    user_main.refresh_token = tokens["refresh_token"]
                    user_main.save()
                    success_response = self.token.set_cookie(success_response, tokens)
                    return success_response
        except Exception as e:
            logger.error(f"회원가입 실패 : {e}")
            if isinstance(e, ValidationError):
                error_response = {"message": e.detail}
            else:
                error_response = {"message": str(e)}
            return Response(
                {"message": "회원가입 실패", "data": error_response},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserRefreshView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = Token()

    def get(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"message": "리프레시 토큰이 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            payload_dict = self.token.verify_token(refresh_token)
            if not payload_dict:
                return Response(
                    {"message": "리프레시 토큰이 유효하지 않습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            payload = SimpleNamespace(**payload_dict)
            user_main = UserMain.objects.get(id=payload.id)
            if user_main.refresh_token and user_main.refresh_token != refresh_token:
                return Response(
                    {"message": "리프레시 토큰이 유효하지 않습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            tokens = self.token.set_token(user_main)
            response = Response(
                {"message": "토큰 갱신 성공"},
                status=status.HTTP_200_OK,
            )
            response = self.token.set_cookie(response, tokens)
            return response
        except Exception as e:
            logger.error(f"UserRefreshView 오류: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserFriendView(APIView):
    def get(self, request):
        try:
            user_main = UserMain.objects.select_related("userprofile").get(
                id=request.token_user.id
            )
            user_main = user_main.my_friend.all()
            serializer = UserMainSerializer(user_main, many=True)
            success_response = Response(
                {"message": "친구 목록 조회 성공", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
            return success_response
        except Exception as e:
            logger.error(f"UserFriendView 오류: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserChannelView(APIView):
    def get(self, request):
        try:
            user_main = UserMain.objects.select_related("userprofile").get(
                id=request.token_user.id
            )
            channels = user_main.channels.all()
            serializer = UserChannelSerializer(channels, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"UserChannelView 오류: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserRequestFriendView(APIView):
    def post(self, request):
        try:
            user_name = request.data.get("userName")

            request_user = UserMain.objects.select_related("userprofile").get(
                name=user_name
            )

            user_main = UserMain.objects.select_related("userprofile").get(
                id=request.token_user.id
            )
            if user_main.my_friend.filter(to_user=request_user).exists():
                return Response(
                    {"message": "이미 친구입니다."}, status=status.HTTP_400_BAD_REQUEST
                )
            UserFriend.objects.create(
                from_user=user_main,
                to_user=request_user,
                status=FriendStatus.PENDING,
            )
            return Response(
                {"message": "친구 요청 성공"},
                status=status.HTTP_200_OK,
            )
        except UserMain.DoesNotExist:
            return Response(
                {"message": "사용자가 존재하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserReceivedFriendRequestView(APIView):
    def get(self, request):
        try:
            requests = UserFriend.objects.filter(
                to_user=request.token_user.id, status=FriendStatus.PENDING
            )
            serializer = UserFriendSerializer(requests, many=True)
            success_response = Response(
                {
                    "message": "친구 요청 목록 조회 성공",
                    "list": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
            return success_response
        except UserFriend.DoesNotExist:
            return Response(
                {"message": "친구 요청 목록이 존재하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserAcceptFriendView(APIView):
    def post(self, request):
        try:
            request_user_id = request.data.get("RequestUserId")

            user_friend = UserFriend.objects.get(
                from_user=request_user_id, to_user=request.token_user.id
            )
            user_friend.status = FriendStatus.ACCEPTED
            user_friend.save(update_fields=["status"])
            return Response(
                {"message": "친구 요청 수락 성공"}, status=status.HTTP_200_OK
            )
        except UserFriend.DoesNotExist:
            return Response(
                {"message": "친구 요청이 존재하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserRejectFriendView(APIView):
    def post(self, request):
        try:
            request_user_id = request.data.get("RequestUserId")

            user_friend = UserFriend.objects.get(
                from_user=request_user_id, to_user=request.token_user.id
            )
            user_friend.status = FriendStatus.REJECTED
            user_friend.save(update_fields=["status"])
            return Response(
                {"message": "친구 요청 거절 성공"}, status=status.HTTP_200_OK
            )
        except UserFriend.DoesNotExist:
            return Response(
                {"message": "친구 요청이 존재하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
