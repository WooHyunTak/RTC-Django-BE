from cassandra.cqlengine import columns
from cassandra.cqlengine import models as cassandra_models
from django.db import models

from user.models import UserMain


class UserChannel(models.Model):
    name = models.CharField(
        max_length=255, null=False, blank=False, help_text="채널 이름"
    )
    description = models.TextField(null=True, blank=True, help_text="채널 설명")
    created_by = models.ForeignKey(
        UserMain, on_delete=models.CASCADE, help_text="채널 생성자"
    )
    is_private = models.BooleanField(default=False, help_text="채널 공개 여부")
    type = models.CharField(
        max_length=10,
        help_text="채널 유형",
        null=True,
        blank=True,
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


class UserChannelMessage(cassandra_models.Model):
    # 파티션키: 채널 이름
    channel_id = columns.Text(primary_key=True)
    # 클러스터키: 메시지 아이디, 메시지
    message_id = columns.TimeUUID(primary_key=True, clustering_order="DESC")
    from_user = columns.Text()  # 메시지 작성자
    message = columns.Text()  # 메시지 내용
    # 메시지 생성일
    created_at = columns.DateTime()
    # 메시지 수정일
    updated_at = columns.DateTime()

    class Meta:
        table_name = "user_channel_message"
