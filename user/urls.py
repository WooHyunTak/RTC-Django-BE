from django.urls import path

from .views import (
    UserAcceptFriendView,
    UserChannelView,
    UserFriendView,
    UserGetMeView,
    UserLogoutView,
    UserMainLoginView,
    UserRefreshView,
    UserRequestFriendListView,
    UserRequestFriendView,
    UserSignUpView,
)

app_name = "user"
urlpatterns = [
    path("login/", UserMainLoginView.as_view(), name="login"),  # 로그인
    path("logout/", UserLogoutView.as_view(), name="logout"),  # 로그아웃
    path("signup/", UserSignUpView.as_view(), name="signup"),  # 회원가입
    path("me/", UserGetMeView.as_view(), name="me"),  # 내 정보 조회
    path("refresh/", UserRefreshView.as_view(), name="refresh"),  # 토큰 갱신
    path("my-friend/", UserFriendView.as_view(), name="friend"),  # 내 친구 목록 조회
    path("my-channel/", UserChannelView.as_view(), name="channel"),  # 내 채널 목록 조회
    path(
        "request-friend/", UserRequestFriendView.as_view(), name="request_friend"
    ),  # 친구 요청
    path(
        "accept-friend/", UserAcceptFriendView.as_view(), name="accept_friend"
    ),  # 친구 수락
    path(
        "request-friend-list/",  # 친구 요청 목록 조회
        UserRequestFriendListView.as_view(),
        name="request_friend_list",
    ),
]
