import os
from uuid import uuid4

import boto3
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from message.models import AttachmentType, MessageAttachment
from rtc_django_chat.settings import AWS_STORAGE_BUCKET_NAME


class FileUploadView(APIView):
    def post(self, request):
        file_list = request.FILES.getlist("file")
        if not file_list:
            return Response(
                {"message": "File not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        s3 = boto3.client("s3")

        attachments_to_create = []
        response_items = []

        for file in file_list:
            ext = os.path.splitext(file.name)[1].lower()
            key = f"uploads/{uuid4().hex}{ext}"

            s3.put_object(
                Body=file,
                Bucket=AWS_STORAGE_BUCKET_NAME,
                Key=key,
            )

            file_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{key}"

            attachments_to_create.append(
                MessageAttachment(
                    url=file_url,
                    name=file.name,
                    size=file.size,
                    type=AttachmentType.FILE,
                )
            )
            response_items.append(
                {
                    "url": file_url,
                    "name": file.name,
                    "size": file.size,
                    "type": AttachmentType.FILE,
                }
            )

        MessageAttachment.objects.bulk_create(attachments_to_create)

        return Response(
            {"message": "File uploaded", "attachments": response_items},
            status=status.HTTP_200_OK,
        )
