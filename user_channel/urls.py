from django.urls import path
from .views import UserChannelCreateView, UserChannelJoinView, UserChannelLeaveView

app_name = "user_channel"
urlpatterns = [
    path("", UserChannelCreateView.as_view(), name="create"),
    path("join/<int:pk>/", UserChannelJoinView.as_view(), name="join"),
    path("leave/<int:pk>/", UserChannelLeaveView.as_view(), name="leave"),
]
