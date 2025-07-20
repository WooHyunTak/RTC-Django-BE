from django.urls import path
from .views import (
    UserChannelCreateView,
    UserChannelJoinView,
    UserChannelLeaveView,
    UserChannelInviteURLView,
)

app_name = "user_channel"
urlpatterns = [
    path("", UserChannelCreateView.as_view(), name="create"),  # 채널 생성
    path("join/<int:pk>/", UserChannelJoinView.as_view(), name="join"),  # 채널 참여
    path("leave/<int:pk>/", UserChannelLeaveView.as_view(), name="leave"),  # 채널 탈퇴
    path(
        "create-invite/<int:pk>/",
        UserChannelInviteURLView.as_view(),
        name="create_invite",
    ),  # 채널 초대 URL 생성
    path(
        "join/<int:pk>/<str:encoded_user_id>/",
        UserChannelJoinView.as_view(),
        name="join_with_encoded_user_id",
    ),  # 채널 초대 URL 참여
]
