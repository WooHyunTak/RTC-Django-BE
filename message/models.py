from django.db import models

from user.models import UserMain
from user_channel.models import UserChannel

# Create your models here.


class MessageType(models.TextChoices):
    NORMAL = "normal", "Normal"
    SYSTEM = "system", "System"
    BOT = "bot", "Bot"


class AttachmentType(models.TextChoices):
    IMAGE = "image", "Image"
    VIDEO = "video", "Video"
    FILE = "file", "File"


class MessageStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    READY = "ready", "Ready"
    FAILED = "failed", "Failed"


class Message(models.Model):
    content = models.TextField(help_text="메시지 내용 html 형식")
    clean_content = models.TextField(help_text="메시지 내용 텍스트 형식")

    type = models.CharField(
        max_length=10,
        choices=MessageType.choices,
        default=MessageType.NORMAL,
        help_text="메시지 유형",
    )
    status = models.CharField(
        max_length=10,
        choices=MessageStatus.choices,
        default=MessageStatus.PENDING,
        help_text="메시지 상태",
    )
    from_user = models.ForeignKey(
        UserMain,
        related_name="sent_messages",
        on_delete=models.CASCADE,
        help_text="메시지 작성자",
    )
    channel = models.ForeignKey(
        UserChannel,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text="채널",
        null=True,
        blank=True,
    )
    root_message = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="thread_replies",
        help_text="스레드 루트 메시지",
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="메시지 생성일")
    updated_at = models.DateTimeField(auto_now=True, help_text="메시지 수정일")

    def __str__(self):
        return self.clean_content

    class Meta:
        db_table = "message"
        indexes = [
            models.Index(fields=["channel", "created_at"]),
            models.Index(fields=["from_user"]),
        ]


class MessageAttachment(models.Model):
    message = models.ForeignKey(
        Message,
        related_name="attachments",
        on_delete=models.CASCADE,
        help_text="첨부된 메시지",
    )
    type = models.CharField(
        max_length=20,
        choices=AttachmentType.choices,
        help_text="첨부 유형",
    )
    url = models.URLField(help_text="파일 URL (S3)")
    name = models.CharField(
        max_length=255, null=True, blank=True, help_text="파일 이름"
    )
    size = models.BigIntegerField(
        null=True, blank=True, help_text="파일 크기 (byte 단위)"
    )
    metadata = models.JSONField(default=dict, blank=True, help_text="추가 메타데이터")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "message_attachment"
        indexes = [models.Index(fields=["message"])]
