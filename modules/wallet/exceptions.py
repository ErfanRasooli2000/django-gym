from rest_framework import status
from rest_framework.exceptions import APIException


class LowWalletBalance(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Wallet balance is lower than transaction amount"
    default_code = "low_wallet_balance"

class TransferFailed(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Transfer Failed."
    default_code = "transfer_failed"