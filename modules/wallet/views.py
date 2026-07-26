import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
def api_home(request):

    body = request.body
    data = {}

    try:
        data = json.loads(body)
    except:
        print("Wrong format")

    print(data.keys())
    print(request.headers)
    return JsonResponse(data)
    return JsonResponse(data)

    return JsonResponse({'message': 'Welcome to Wallet!'})
