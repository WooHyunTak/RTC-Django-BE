from django.urls import path

from .views import (
    UserChannelCreateView,
    UserChannelDetailView,
    UserChannelInviteURLView,
    UserChannelJoinView,
    UserChannelLeaveView,
    UserChannelListView,
    UserChannelMessageView,
    UserDMChannelListView,
)

app_name = "channels"
urlpatterns = [
    path("", UserChannelCreateView.as_view(), name="create"),  # 채널 생성
    path(
        "my-channels/", UserChannelListView.as_view(), name="my_channels"
    ),  # 채널 목록 조회
    path("<int:pk>/", UserChannelDetailView.as_view(), name="detail"),  # 채널 상세 조회
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
    path(
        "<int:pk>/messages/",
        UserChannelMessageView.as_view(),
        name="messages",
    ),  # 채널 메시지 조회
    path(
        "direct-messages/",
        UserDMChannelListView.as_view(),
        name="direct_messages",
    ),  # 사용자 다이렉트 메시지 채널 조회
]
