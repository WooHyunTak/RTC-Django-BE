import logging

from django.shortcuts import render

from django.db import transaction
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from .models import UserMain, UserProfile
from .serializers import UserMainSerializer, UserMainCreateSerializer
from common.utils.tokens import Token

logger = logging.getLogger(__name__)


class UserMainLoginView(APIView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = Token()

    def post(self, request):
        try:
            login_email = request.data.get("loginEmail")
            login_password = request.data.get("loginPassword")
            user_main = UserMain.objects.select_related("userprofile").get(
                email=login_email
            )
            serializer = UserMainSerializer(user_main)
            if user_main.password == login_password:
                cookie = self.set_token(user_main)
                success_response = Response(
                    {
                        "message": "로그인 성공",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
                success_response.set_cookie(
                    key="access_token", value=cookie["access_token"], httponly=True
                )
                success_response.set_cookie(
                    key="refresh_token", value=cookie["refresh_token"], httponly=True
                )
                return success_response
            else:
                return Response(
                    {"message": "로그인 실패"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"UserMainLoginView 오류: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def set_token(self, user):
        token = self.token.generate_token(user)
        access_token = token["access_token"]
        refresh_token = token["refresh_token"]
        cookie = {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
        return cookie


class UserGetMeView(APIView):
    def get(self, request):
        try:
            # 미들웨어에서 설정한 token_user가 있는지 확인
            if hasattr(request, "user"):
                print("request.user", request.user)
                user_main = UserMain.objects.select_related("userprofile").get(
                    id=request.user.id
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
                serializer = UserMainCreateSerializer(data=user_data)
                if serializer.is_valid():
                    # 유저 생성
                    user_main = serializer.save()
                    # 유저 프로필 생성
                    if request.data.get("imageUrl", None):
                        UserProfile.objects.create(
                            user=user_main,
                            image_url=request.data.get("imageUrl", None),
                        )
                    cookie = self.set_token(user_main)
                    data = serializer.data
                    data.pop("password", None)
                    success_response = Response(
                        {"message": "회원가입 성공", "data": data},
                        status=status.HTTP_201_CREATED,
                    )
                    success_response.set_cookie(
                        key="access_token",
                        value=cookie["access_token"],
                        httponly=True,
                        samesite="None",
                        secure=True,
                    )
                    success_response.set_cookie(
                        key="refresh_token",
                        value=cookie["refresh_token"],
                        httponly=True,
                        samesite="None",
                        secure=True,
                    )
                    return success_response
                else:
                    return Response(
                        {"message": "회원가입 실패"}, status=status.HTTP_400_BAD_REQUEST
                    )
        except Exception as e:
            logger.error(f"UserSignUpView 오류: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def set_token(self, user):
        token = self.token.generate_token(user)
        access_token = token["access_token"]
        refresh_token = token["refresh_token"]
        cookie = {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
        return cookie
