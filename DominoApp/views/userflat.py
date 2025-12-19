from math import fabs
import stat
from urllib import response
from django.shortcuts import get_object_or_404
from django.urls import is_valid_path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Building, Flat, UserFlat, UserFlatRole
from ..serializer import FlatSerializer, UserFlatSerializer
from DominoApp import serializer
from DominoApp.utils import get_authenticated_user


@api_view(['GET', 'POST'])
def userflat_list(request, building_id, flat_id):

    building = get_object_or_404(Building, pk=building_id)
    flat = get_object_or_404(Flat, pk=flat_id, BuildingId=building)

    
    if request.method == 'GET':
        userflats = UserFlat.objects.filter(FlatId=flat)
        serializer = UserFlatSerializer(userflats, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        user, error_response = get_authenticated_user(request, required_role='ADMIN')
        if error_response:
            return error_response
        
        data = request.data.copy()
        data['FlatId'] = flat.FlatId 
        
        role = data.get('UserFlatRole')
        if not role:
            role = UserFlatRole.TENANT
            data['UserFlatRole'] = role

        if role == UserFlatRole.OWNER:
            existing_owner = UserFlat.objects.filter(
                FlatId=flat,
                UserFlatRole=UserFlatRole.OWNER,
                UserFlatDateTo__isnull=True
            ).exists()

            if existing_owner:
                return Response(
                    {"error": "This flat already has an active owner"},
                    status=400
                )

        serializer = UserFlatSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
def userflat_detail(request, building_id, flat_id, userflat_id):

    building = get_object_or_404(Building, pk=building_id)
    flat = get_object_or_404(Flat, pk=flat_id, BuildingId=building)
    userflat = get_object_or_404(UserFlat, pk=userflat_id, FlatId=flat)


    if request.method == 'GET':
        serializer = UserFlatSerializer(userflat)
        return Response(serializer.data)

    if request.method == 'PUT':
        user, error_response = get_authenticated_user(request, required_role='ADMIN')
        if error_response:
            return error_response
        
        data = request.data.copy()
        data['FlatId'] = flat.FlatId   

        role = data.get('UserFlatRole', userflat.UserFlatRole)
        if not role:
            role = UserFlatRole.TENANT
            data['UserFlatRole'] = role

        if role == UserFlatRole.OWNER:
            existing_owner = UserFlat.objects.filter(
                FlatId=flat,
                UserFlatRole=UserFlatRole.OWNER,
                UserFlatDateTo__isnull=True
            ).exclude(pk=userflat.pk)
            if existing_owner.exists():
                return Response(
                    {"error": "This flat already has an active owner"},
                    status=400
                )

        serializer = UserFlatSerializer(userflat, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        user, error_response = get_authenticated_user(request, required_role='ADMIN')
        if error_response:
            return error_response
        
        userflat.delete()
        return Response(status=204)
