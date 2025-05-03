from django.urls import path, include
from .views import UserMainLoginView, UserSignUpView, UserGetMeView, UserRefreshView

app_name = "user"
urlpatterns = [
    path("login/", UserMainLoginView.as_view(), name="login"),
    path("signup/", UserSignUpView.as_view(), name="signup"),
    path("me/", UserGetMeView.as_view(), name="me"),
    path("refresh/", UserRefreshView.as_view(), name="refresh"),
]
