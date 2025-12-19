from math import fabs
import stat
from django.shortcuts import render
from django.urls import is_valid_path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Announ, User
from ..serializer import AnnounSerializer
from DominoApp import serializer
from DominoApp.utils import get_authenticated_user

@api_view(['GET', 'POST'])
def get_announ(request):
    if request.method == 'GET':
        announs = Announ.objects.all()
        serializer = AnnounSerializer(announs, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        user, error_response = get_authenticated_user(request, required_role='ADMIN')
        if error_response:
            return error_response
        
        data = request.data.copy()
        data["UserId"] = user.UserId
        serializer = AnnounSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def announ_detail(request, pk):
    try:
        announ = Announ.objects.get(pk=pk)
    except Announ.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = AnnounSerializer(announ)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        user, error_response = get_authenticated_user(request, required_role='ADMIN')
        if error_response:
            return error_response
        
        data = request.data.copy()
        data["UserId"] = announ.UserId_id
        serializer = AnnounSerializer(announ, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        user, error_response = get_authenticated_user(request, required_role='ADMIN')
        if error_response:
            return error_response
        
        announ.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
