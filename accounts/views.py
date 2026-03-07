from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import UserRegistrationSerializer
from rest_framework.decorators import api_view

# Create your views here.
@api_view(['POST'])
def register_user(request):
    serialize = UserRegistrationSerializer(data=request.data)
    if serialize.is_valid():
        serialize.save()
        return Response(serialize.data)
    return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)
