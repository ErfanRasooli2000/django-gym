from rest_framework.pagination import CursorPagination

class TransactionCursorPagination(CursorPagination):
    page_size = 10
    ordering = '-id'