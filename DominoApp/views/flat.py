from math import fabs
import stat
from tarfile import data_filter
from urllib import response
from django.shortcuts import render
from django.urls import is_valid_path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Building, Flat
from ..serializer import FlatSerializer
from DominoApp import serializer
from DominoApp.utils import get_authenticated_user


@api_view(['GET', 'POST'])
def building_flats(request, building_id):

    try:
        building = Building.objects.get(pk=building_id)
    except Building.DoesNotExist:
        return Response({"error": "Building not found"}, status=404)

    if request.method == 'GET':
        flats = Flat.objects.filter(BuildingId=building)
        serializer = FlatSerializer(flats, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        user, error_response = get_authenticated_user(request, required_role='ADMIN')
        if error_response:
            return error_response
        
        data = request.data.copy()
        data["BuildingId"] = building.BuildingId

        serializer = FlatSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


@api_view(['GET','PUT', 'DELETE'])
def flat_detail(request, building_id, flat_id):

    try:
        building = Building.objects.get(pk=building_id)
    except Building.DoesNotExist:
        return Response({"error": "Building not found"}, status=404)

    try:
        flat = Flat.objects.get(pk=flat_id, BuildingId=building)
    except Flat.DoesNotExist:
        return Response({"error": "Flat not found in this building"}, status=404)

    if request.method == 'GET':
        serializer = FlatSerializer(flat)
        return Response(serializer.data)

    if request.method == 'PUT':
        user, error_response = get_authenticated_user(request, required_role='ADMIN')
        if error_response:
            return error_response
        
        serializer = FlatSerializer(flat, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        user, error_response = get_authenticated_user(request, required_role='ADMIN')
        if error_response:
            return error_response
        
        flat.delete()
        return Response(status=204)