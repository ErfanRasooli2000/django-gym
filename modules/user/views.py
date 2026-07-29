from rest_framework import generics, permissions
from modules.user.models import User
from .serializers import UserRegisterSerializer

class ListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

class RetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer