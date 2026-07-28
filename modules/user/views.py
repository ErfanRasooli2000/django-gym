from rest_framework.permissions import AllowAny
from modules.user.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view, parser_classes, permission_classes
from .serializers import UserRegisterSerializer

@api_view(["GET"])
@permission_classes([AllowAny])
def single_user(request , *args , **kwargs):

    users = User.objects.all().order_by("?")

    return Response(UserRegisterSerializer(users , many=True).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def create(request):

    serializer = UserRegisterSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    serializer.save()

    return Response(serializer.data)

    pass