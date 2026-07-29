from django.urls import path
from .views import ListCreateApiView, RetrieveUpdateDestroyApiView

urlpatterns = [
    path("" , ListCreateApiView.as_view()),
    path("<int:pk>" , RetrieveUpdateDestroyApiView.as_view()),
]