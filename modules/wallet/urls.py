from django.urls import path
from . import views

urlpatterns = [
    path('balance' , views.balance),
    path('transactions' , views.transactions),
    path('transfer' , views.transfer),
]