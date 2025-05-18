from django.urls import path, include
from .views import (
    UserMainLoginView,
    UserSignUpView,
    UserGetMeView,
    UserRefreshView,
    UserFriendView,
    UserChannelView,
    UserRequestFriendView,
    UserAcceptFriendView,
    UserRequestFriendListView,
    UserLogoutView,
)

app_name = "user"
urlpatterns = [
    path("login/", UserMainLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("signup/", UserSignUpView.as_view(), name="signup"),
    path("me/", UserGetMeView.as_view(), name="me"),
    path("refresh/", UserRefreshView.as_view(), name="refresh"),
    path("my-friend/", UserFriendView.as_view(), name="friend"),
    path("my-channel/", UserChannelView.as_view(), name="channel"),
    path("request-friend/", UserRequestFriendView.as_view(), name="request_friend"),
    path("accept-friend/", UserAcceptFriendView.as_view(), name="accept_friend"),
    path(
        "request-friend-list/",
        UserRequestFriendListView.as_view(),
        name="request_friend_list",
    ),
]
