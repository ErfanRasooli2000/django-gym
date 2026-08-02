from django.urls import path
from modules.user.views import ListCreateUserApiView, RetrieveUpdateDestroyUserApiView

urlpatterns = [
    path("" , ListCreateUserApiView.as_view()),
    path("<int:pk>" , RetrieveUpdateDestroyUserApiView.as_view()),
]