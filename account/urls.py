from django.urls import path, include
from . import views

urlpatterns = [
    path('check', views.CheckAPI.as_view()),
    path('create', views.CreateAPI.as_view()),
    path('otp', views.OTPAPI.as_view()),
    path('otp/disabled', views.OTPDisabledAPI.as_view()),
    path('me', views.MeAPI.as_view()),
    path('config', views.ConfigAPI.as_view()),
    path('leverage', views.LeverageAPI.as_view()),
    path('max-size', views.MaxSizeAPI.as_view()),
    path('max-avail-size', views.MaxAvailSizeAPI.as_view()),
    path('fee-rate', views.FeeRateAPI.as_view()),
    path('level', views.LevelAPI.as_view()),
    path('login/history', views.LoginHistoryAPI.as_view()),
    path('freeze', views.FreezeAPI.as_view()),
    path('kyc/link', views.KYCAPI.as_view()),
    path('accept/create', views.AcceptAPI.as_view()),
    path('accept/delete', views.AcceptRemoveAPI.as_view())
]