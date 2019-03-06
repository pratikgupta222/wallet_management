from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from wallet import views


urlpatterns = [
    path('wallet_txn', views.WalletTransaction.as_view(), name='wallet-transaction'),
    path('wallet_balance', views.WalletBalance.as_view(), name='wallet-balance'),
    path('wallet_history', views.WalletHistory.as_view(), name='wallet-history'),
    # url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='user-detail'),
]
