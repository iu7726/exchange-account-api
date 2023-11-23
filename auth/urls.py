from django.urls import path, include
from . import views
from knox.views import LogoutAllView, LogoutView

urlpatterns = [
    path('token/refresh', views.AuthTokenAPI.as_view()),
    path('token', views.LoginOtpAPI.as_view()),
    path('logout', LogoutView.as_view()),
    path('logout-all', LogoutAllView.as_view())
]