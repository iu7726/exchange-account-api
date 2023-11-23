from django.urls import path, include
from . import views

urlpatterns = [
    path('deposit', views.DepositAPI.as_view()),
    path('withdraw', views.WithdrawAPI.as_view()),
    path('alert', views.AlertAPI.as_view())
]