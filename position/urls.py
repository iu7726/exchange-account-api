from django.urls import path, include
from . import views

urlpatterns = [
    path('open', views.OpenPositionAPI.as_view()),
    path('history', views.PositionHistoryAPI.as_view()),
    path('risk', views.PositionRiskAPI.as_view()),
    path('mode', views.PostionModeAPI.as_view())
]