from django.db import models
from user.models import UserMain

class UserChannel(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, help_text="채널 이름")
    description = models.TextField(null=True, blank=True, help_text="채널 설명")
    created_by = models.ForeignKey(
        UserMain, on_delete=models.CASCADE, help_text="채널 생성자"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="생성일")
    updated_at = models.DateTimeField(auto_now=True, help_text="수정일")
    members = models.ManyToManyField(
        UserMain,
        through="UserChannelMember",
        related_name="channels",
        help_text="참여 사용자",
    )

    class Meta:
        db_table = "user_channel"

class UserChannelMember(models.Model):
    channel = models.ForeignKey(
        UserChannel,
        on_delete=models.CASCADE,
        related_name="channel_memberships",
        help_text="채널 참여 관계",
    )
    user = models.ForeignKey(
        UserMain,
        on_delete=models.CASCADE,
        related_name="user_memberships",
        help_text="사용자 채널 참여 관계",
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="참여일")
    updated_at = models.DateTimeField(auto_now=True, help_text="수정일")

    class Meta:
        db_table = "user_channel_member"
        unique_together = (("channel", "user"),)

