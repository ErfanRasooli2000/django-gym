from django.urls import path
from modules.wallet import views

urlpatterns = [
    path('balance' , views.balance),
    path('transactions' , views.transactions),
    path('transfer' , views.transfer),
    path('test' , views.test),
]