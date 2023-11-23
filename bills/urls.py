from django.urls import path, include
from . import views

urlpatterns = [
    path('history', views.BillsAPI.as_view()),
    path('archive', views.BillsArchiveAPI.as_view()),
]