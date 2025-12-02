from math import fabs
from django.shortcuts import render
from django.urls import is_valid_path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User, Building, Flat, UserFlat, Rent, Report, Announ
from .serializer import UserFlatSerializer, BuildingSerializer, FlatSerializer, UserSerializer, RentSerializer, ReportSerializer, AnnounSerializer
from DominoApp import serializer

@api_view(['GET'])
def get_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
