from django.db import models


class UserMain(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        null=False,
        blank=False,
        help_text="사용자 이름",
    )
    email = models.EmailField(
        unique=True, null=False, blank=False, help_text="로그인 이메일"
    )
    password = models.CharField(
        max_length=255, null=False, blank=False, help_text="비밀번호"
    )
    refresh_token = models.CharField(
        max_length=255, null=True, blank=True, help_text="마지막 리프레시 토큰"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="생성일")
    updated_at = models.DateTimeField(auto_now=True, help_text="수정일")
    friends = models.ManyToManyField(
        "self",
        through="UserFriend",
        symmetrical=False,
        related_name="friend_of",
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "user_main"


class UserProfile(models.Model):
    user = models.OneToOneField(UserMain, on_delete=models.CASCADE)
    image_url = models.CharField(
        max_length=255, null=True, blank=True, help_text="프로필 이미지"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="생성일")
    updated_at = models.DateTimeField(auto_now=True, help_text="수정일")

    def __str__(self):
        return f"{self.user.name} Profile"

    class Meta:
        db_table = "user_profile"


class FriendStatus(models.TextChoices):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class UserFriend(models.Model):
    from_user = models.ForeignKey(
        UserMain, related_name="my_friend", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        UserMain, related_name="received_friend", on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=255,
        choices=FriendStatus.choices,
        default=FriendStatus.PENDING,
        help_text="친구 상태",
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="생성일")
    updated_at = models.DateTimeField(auto_now=True, help_text="수정일")

    class Meta:
        db_table = "user_friend"
        unique_together = (("from_user", "to_user"),)
