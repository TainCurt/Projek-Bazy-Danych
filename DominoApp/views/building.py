from math import fabs
import stat
from tarfile import data_filter
from django.shortcuts import render
from django.urls import is_valid_path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Building
from ..serializer import BuildingSerializer
from DominoApp import serializer

@api_view(['GET', 'POST'])
def get_buildings(request):
    if request.method == 'GET':
        users = Building.objects.all()
        serializer = BuildingSerializer(users, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = BuildingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def building_detail(request, pk):
    try:
        building = Building.objects.get(pk=pk)
    except Building.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = BuildingSerializer(building)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = BuildingSerializer(building, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        building.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
