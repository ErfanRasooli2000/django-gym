from django.core.cache import cache
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from modules.wallet.serializers import WalletTransactionSerializer, TransferSerializer
from modules.wallet.services import transfer_wallet
from modules.wallet.pagination import TransactionCursorPagination

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def balance(request):

    wallet = request.user.wallet

    if wallet is None:
        return Response({"message": "User Wallet Not Found"}, status=status.HTTP_404_NOT_FOUND)

    return Response({"balance": wallet.balance}, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def transactions(request):

    wallet = request.user.wallet

    if wallet is None:
        return Response({"message": "User Wallet Not Found"}, status=status.HTTP_404_NOT_FOUND)

    paginator = TransactionCursorPagination()
    queryset = wallet.transactions.all()
    page = paginator.paginate_queryset(queryset , request)
    serializer = WalletTransactionSerializer(page, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def transfer(request):

    wallet = request.user.wallet

    if wallet is None:
        return Response({"message": "User Wallet Not Found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = TransferSerializer(data=request.data , context={"request": request})
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    if transfer_wallet(wallet , data['to_wallet'] , data['amount'] , data['idempotency_key']) is None:
        return Response({"message": "Transfer Success"}, status=status.HTTP_201_CREATED)

    return Response({"message": "Transfer Failed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def test(request):
    cache.set("mamad" , "akbar" , 100)
    return Response({"message": "test"}, status=status.HTTP_200_OK)