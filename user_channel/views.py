from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserChannelCreateSerializer, UserChannelSerializer
from .models import UserChannel

import logging

logger = logging.getLogger(__name__)


class UserChannelCreateView(APIView):
    def post(self, request):
        try:
            created_by = request.token_user.id
            serializer = UserChannelCreateSerializer(
                data=request.data, context={"created_by": created_by}
            )
            if serializer.is_valid():
                serializer.save()
                success_response = Response(
                    {"message": "채널 생성 성공", "data": serializer.data},
                    status=status.HTTP_201_CREATED,
                )
                return success_response
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"UserChannelCreateView 오류: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
        except Exception as e:
            print(f"UserChannelJoinView 오류: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
        except Exception as e:
            print(f"UserChannelLeaveView 오류: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
