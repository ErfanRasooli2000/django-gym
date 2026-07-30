from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAdminUser
from modules.user.models import User
from .serializers import UserRegisterSerializer

class ListCreateUserApiView(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication , TokenAuthentication]
    permission_classes = [IsAdminUser]
    queryset = User.objects.select_related("wallet").all()
    serializer_class = UserRegisterSerializer

class RetrieveUpdateDestroyUserApiView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [SessionAuthentication , TokenAuthentication]
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer