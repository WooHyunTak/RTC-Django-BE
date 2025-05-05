from django.urls import path
from .views import UserChannelCreateView

app_name = "user_channel"
urlpatterns = [
    path("", UserChannelCreateView.as_view(), name="create"),
]
