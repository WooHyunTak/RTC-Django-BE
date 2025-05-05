from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserChannelCreateSerializer

import logging
logger = logging.getLogger(__name__)

class UserChannelCreateView(APIView):
    def post(self, request):
        try:
            created_by = request.token_user.id
            serializer = UserChannelCreateSerializer(data=request.data, context={"created_by": created_by})
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


