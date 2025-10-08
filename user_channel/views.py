import base64
import logging

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from message.models import Message
from user.models import UserMain

from .models import UserChannel, UserChannelMember
from .serializers import (
    UserChannelCreateSerializer,
    UserChannelListSerializer,
    UserChannelMessageSerializer,
    UserChannelSerializer,
    UserDMChannelListSerializer,
)

logger = logging.getLogger(__name__)


class UserChannelListView(APIView):
    def get(self, request):
        try:
            # 로그인 정보
            login_user_id = request.token_user.id
            channels = UserChannel.objects.filter(
                members__id=login_user_id, is_direct=False
            )
            serializer = UserChannelListSerializer(channels, many=True)
            return Response(
                {
                    "message": "success",
                    "list": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except UserChannel.DoesNotExist:
            return Response(
                {"message": "채널 정보를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserChannelCreateView(APIView):
    def post(self, request):
        try:
            created_by = request.token_user.id
            serializer = UserChannelCreateSerializer(
                data=request.data, context={"created_by": created_by}
            )
            if serializer.is_valid():
                # Transaction 시작
                with transaction.atomic():
                    channel = serializer.save()

                    member = UserMain.objects.get(id=created_by)

                    UserChannelMember.objects.get_or_create(
                        channel=channel,
                        user=member,
                    )

                    success_response = Response(
                        {"message": "채널 생성 성공", "data": serializer.data},
                        status=status.HTTP_201_CREATED,
                    )
                    return success_response
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserChannel.DoesNotExist:
            return Response(
                {"message": "채널 정보를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserChannelDetailView(APIView):
    def get(self, request, pk):
        try:
            channel = UserChannel.objects.get(id=pk)
            serializer = UserChannelSerializer(channel)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserChannel.DoesNotExist:
            return Response(
                {"message": "채널 정보를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def post(self, request, pk):
        try:
            channel = UserChannel.objects.get(id=pk)
            serializer = UserChannelSerializer(channel, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserChannel.DoesNotExist:
            return Response(
                {"message": "채널 정보를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, pk):
        try:
            channel = UserChannel.objects.get(id=pk)
            channel.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserChannel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class UserChannelJoinView(APIView):
    def post(self, request, pk):
        try:
            channel = UserChannel.objects.get(id=pk)
            if channel.members.filter(id=request.token_user.id).exists():
                return Response(
                    {"message": "이미 채널에 참여한 사용자입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            channel.members.add(request.token_user.id)
            channel.save()
            serializer = UserChannelSerializer(channel)
            return Response(
                {"message": "채널 참여 성공", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except UserChannel.DoesNotExist:
            return Response(
                {"message": "채널 정보를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserChannelLeaveView(APIView):
    def post(self, request, pk):
        try:
            channel = UserChannel.objects.get(id=pk)
            if channel.members.filter(id=request.token_user.id).exists():
                channel.members.remove(request.token_user.id)
                channel.save()
                return Response(
                    {"message": "채널 탈퇴 성공"}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "채널에 참여하지 않은 사용자입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except UserChannel.DoesNotExist:
            return Response(
                {"message": "채널 정보를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserChannelInviteURLView(APIView):
    def post(self, request, pk):
        try:
            invite_user = UserMain.objects.get(id=request.token_user.id)
            encoded_invite_user = encode_user_id(invite_user.id)
            channel = UserChannel.objects.get(id=pk)
            if not channel:
                return Response(
                    {"message": "채널을 찾을 수 없습니다."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            invite_url = f"{settings.FRONTEND_URL}/api/user-channel/join/{channel.id}/{encoded_invite_user}"
            return Response({"invite_url": invite_url}, status=status.HTTP_200_OK)
        except UserChannel.DoesNotExist:
            return Response(
                {"message": "채널 정보를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserChannelMessageView(APIView):
    limit = 30

    def get(self, request, pk):
        try:
            UserChannel.objects.get(id=pk)
            messages = (
                Message.objects.select_related("from_user")
                .filter(channel_id=pk)
                .order_by("created_at")[: self.limit]
            )
            serializer = UserChannelMessageSerializer(messages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserChannel.DoesNotExist:
            return Response(
                {"message": "채널 정보를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserDMChannelListView(APIView):
    def get(self, request):
        try:
            # 내가 참여한 다이렉트 메시지 채널 조회
            channels = (
                UserChannel.objects.filter(
                    members__id=request.token_user.id,
                    is_direct=True,
                )
                .prefetch_related("members")
                .order_by("created_at")
            )

            serializer = UserDMChannelListSerializer(
                channels, many=True, context={"from_user_id": request.token_user.id}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserChannel.DoesNotExist:
            return Response(
                {"message": "채널 정보를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


def encode_user_id(user_id):
    return base64.b64encode(str(user_id).encode()).decode()


def decode_user_id(encoded_id):
    return int(base64.b64decode(encoded_id.encode()).decode())
