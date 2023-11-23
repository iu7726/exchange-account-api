from django.urls import path, include
from . import views

urlpatterns = [
    path('balance', views.BalanceAccoountAPI.as_view()),
    path('balance/history', views.BalanceHistoryAPI.as_view()),
    path('balance/asset', views.BalanceAssetAPI.as_view()),
    path('deposit', views.DepositAPI.as_view()),
    path('deposit/info', views.DepositInfoAPI.as_view()),
    path('deposit/lightning', views.DepositLightningAPI.as_view()),
    path('deposit-history', views.DepositHistoryAPI.as_view()),
    path('withdraw', views.WithdrawAPI.as_view()),
    path('withdraw/lightning', views.WithdrawLightningAPI.as_view()),
    path('withdraw/info', views.WithdrawInfoAPI.as_view()),
    path('withdraw-history', views.WithdrawHistoryAPI.as_view()),
    path('transfer/state', views.TransferStateAPI.as_view()),
    path('max-withdrawal', views.MaxWithdrawalAPI.as_view()),
    path('transcation/state', views.TranscationStateAPI.as_view()),
    path('currencies', views.CurrenciesAPI.as_view()),
]