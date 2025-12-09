from math import fabs
import stat
from tarfile import data_filter
from django.shortcuts import render
from django.urls import is_valid_path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import User, UserFlat, Flat, Rent, Report, Building
from ..serializer import UserSerializer, FlatSerializer, RentSerializer, ReportSerializer
from DominoApp import serializer
from DominoApp.utils import get_authenticated_user


@api_view(['GET', 'POST'])
def get_users(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        user, error_response = get_authenticated_user(request, required_role='ADMIN')
        if error_response:
            return error_response
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        user, error_response = get_authenticated_user(request, required_role='ADMIN')
        if error_response:
            return error_response
        
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        user, error_response = get_authenticated_user(request, required_role='ADMIN')
        if error_response:
            return error_response
        
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def me(request):

    user, error_response = get_authenticated_user(request)
    if error_response:
        return error_response

    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(['GET'])
def my_flats(request):
    user, error_response = get_authenticated_user(request)
    if error_response:
        return error_response

    user_flats = UserFlat.objects.filter(UserId=user, UserFlatDateTo__isnull=True)
    flats = [uf.FlatId for uf in user_flats]

    serializer = FlatSerializer(flats, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def my_rents(request):

    user, error_response = get_authenticated_user(request)
    if error_response:
        return error_response

    user_flats = UserFlat.objects.filter(UserId=user, UserFlatDateTo__isnull=True)

    flat_ids = [uf.FlatId.FlatId for uf in user_flats]  # pobieramy same ID mieszkań

    rents = Rent.objects.filter(FlatId__in=flat_ids).order_by('-RentYear', '-RentMonth')

    serializer = RentSerializer(rents, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
def my_reports(request):

    user, error_response = get_authenticated_user(request)
    if error_response:
        return error_response

    if request.method == 'GET':
        reports = Report.objects.filter(UserId=user).order_by('-ReportTime')
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data.copy()
        # przypisujemy UserId z tokena a nie z body
        data['UserId'] = user.UserId

        data.pop('ReportStatus', None)

        report_type = data.get('ReportType', 'GENERAL')
        errors = {}

        if report_type == 'FLAT':
            flat_id = data.get('FlatId')

            if not flat_id:
                errors['FlatId'] = ['FlatId is required for FLAT reports.']
            else:
                try:
                    flat = Flat.objects.get(pk=flat_id)
                except Flat.DoesNotExist:
                    errors['FlatId'] = ['Flat does not exist.']
                else:
                    has_relation = UserFlat.objects.filter(
                        UserId=user,
                        FlatId=flat,
                        UserFlatDateTo__isnull=True
                    ).exists()
                    if not has_relation:
                        errors['FlatId'] = ['You are not assigned to this flat.']
                    else:
                        # automatycznie ustawiamy BuildingId zgodnie z mieszkaniem
                        data['BuildingId'] = flat.BuildingId_id

        elif report_type == 'BUILDING':
            building_id = data.get('BuildingId')

            if not building_id:
                errors['BuildingId'] = ['BuildingId is required for BUILDING reports.']
            else:
                try:
                    building = Building.objects.get(pk=building_id)
                except Building.DoesNotExist:
                    errors['BuildingId'] = ['Building does not exist.']
                else:
                    has_flat_in_building = UserFlat.objects.filter(
                        UserId=user,
                        FlatId__BuildingId=building,
                        UserFlatDateTo__isnull=True
                    ).exists()
                    if not has_flat_in_building:
                        errors['BuildingId'] = ['You have no flat in this building.']

            # nie potrzebujemy FlatId dla BUILDING
            data.pop('FlatId', None)

        elif report_type == 'GENERAL':
            data.pop('FlatId', None)
            data.pop('BuildingId', None)

        # zły typ
        else:
            errors['ReportType'] = ['Invalid ReportType. Use FLAT, BUILDING or GENERAL.']

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReportSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


