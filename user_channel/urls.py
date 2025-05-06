from django.urls import path
from .views import (
    UserChannelCreateView,
    UserChannelJoinView,
    UserChannelLeaveView,
    UserChannelInviteURLView,
)

app_name = "user_channel"
urlpatterns = [
    path("", UserChannelCreateView.as_view(), name="create"),
    path("join/<int:pk>/", UserChannelJoinView.as_view(), name="join"),
    path("leave/<int:pk>/", UserChannelLeaveView.as_view(), name="leave"),
    path(
        "create-invite/<int:pk>/",
        UserChannelInviteURLView.as_view(),
        name="create_invite",
    ),
    path(
        "join/<int:pk>/<str:encoded_user_id>/",
        UserChannelJoinView.as_view(),
        name="join_with_encoded_user_id",
    ),
]
