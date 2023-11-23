from django.urls import path, include
from . import views

urlpatterns = [
    path('info', views.SocketInfoAPI.as_view()),
]