from math import fabs
import stat
from tarfile import data_filter
from urllib import response
from django.shortcuts import render
from django.urls import is_valid_path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Building, Flat, User, Rent
from ..serializer import FlatSerializer, UserFlatSerializer, UserSerializer, RentSerializer
from DominoApp import serializer
from DominoApp.utils import get_authenticated_user


@api_view(['GET', 'POST'])
def flat_rent(request, flat_id, building_id):

    try:
        building = Building.objects.get(pk=building_id)
    except Building.DoesNotExist:
        return Response({"error": "Building not found"}, status=404)

    try:
        flat = Flat.objects.get(pk=flat_id, BuildingId=building)
    except Flat.DoesNotExist:
        return Response({"error": "Flat not found in this building"}, status=404)

    if request.method == 'GET':
        rents = Rent.objects.filter(FlatId=flat)
        serializer = RentSerializer(rents, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        user, error_response = get_authenticated_user(request, required_role='ADMIN')
        if error_response:
            return error_response
    
        data = request.data.copy()
        data["FlatId"] = flat.FlatId

        serializer = RentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)



@api_view(['GET', 'PUT', 'DELETE'])
def flat_rent_detail(request, building_id, flat_id, rent_id):

    try:
        building = Building.objects.get(pk=building_id)
    except Building.DoesNotExist:
        return Response({"error": "Building not found"}, status=404)
    
    try:
        flat = Flat.objects.get(pk=flat_id, BuildingId=building)
    except Flat.DoesNotExist:
        return Response({"error": "Flat not found in this building"}, status=404)

    try:
        rent = Rent.objects.get(pk=rent_id, FlatId=flat)
    except Rent.DoesNotExist:
        return Response({"error": "Rent not found for this flat"}, status=404)

    if request.method == 'GET':
        serializer = RentSerializer(rent)
        return Response(serializer.data)

    if request.method == 'PUT':
        user, error_response = get_authenticated_user(request, required_role='ADMIN')
        if error_response:
            return error_response
        
        data = request.data.copy()
        data['FlatId'] = flat.FlatId   

        serializer = RentSerializer(rent, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        user, error_response = get_authenticated_user(request, required_role='ADMIN')
        if error_response:
            return error_response
        
        rent.delete()
        return Response(status=204)
