from rest_framework import generics, permissions
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from modules.user.models import User
from .permissions import CanCRUDUser
from .serializers import UserRegisterSerializer

class ListCreateApiView(generics.ListCreateAPIView):
    authentication_classes = [SessionAuthentication , TokenAuthentication]
    permission_classes = [CanCRUDUser]
    queryset = User.objects.select_related("wallet").all()
    serializer_class = UserRegisterSerializer

class RetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [SessionAuthentication , TokenAuthentication]
    permission_classes = [CanCRUDUser]
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer