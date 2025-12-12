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
from django.db.models import Q

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

@api_view(['GET', 'PATCH', 'DELETE'])
def user_detail(request, pk):
    try:
        target_user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # admin-only dla operacji na userach
    auth_user, error_response = get_authenticated_user(request, required_role='ADMIN')
    if error_response:
        return error_response

    if request.method == 'GET':
        serializer = UserSerializer(target_user)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = UserSerializer(target_user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        target_user.delete()
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

    # 1) aktywne relacje user -> flat
    user_flats_qs = UserFlat.objects.filter(UserId=user, UserFlatDateTo__isnull=True)
    flat_ids = list(user_flats_qs.values_list('FlatId_id', flat=True))

    # jeśli user nie ma mieszkań zwracamy pusta liste
    if not flat_ids:
        return Response([], status=status.HTTP_200_OK)

    # 2) filtr flat_id z query params
    flat_id_param = request.query_params.get('flat_id')
    if flat_id_param is not None:
        try:
            flat_id_int = int(flat_id_param)
        except ValueError:
            return Response(
                {"flat_id": ["flat_id must be an integer."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        # autoryzacja czy user ma dostęp do tego mieszkania
        if flat_id_int not in flat_ids:
            return Response(
                {"error": "You are not assigned to this flat."},
                status=status.HTTP_403_FORBIDDEN
            )

        rents = Rent.objects.filter(FlatId_id=flat_id_int).order_by('-RentYear', '-RentMonth')
    else:
        # bez filtra -> wszystkie naliczenia dla mieszkan uzytkownika
        rents = Rent.objects.filter(FlatId_id__in=flat_ids).order_by('-RentYear', '-RentMonth')

    serializer = RentSerializer(rents, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def my_reports(request):

    user, error_response = get_authenticated_user(request)
    if error_response:
        return error_response

    if request.method == 'GET':
        # query params
        flat_id_param = request.query_params.get('flat_id')
        building_id_param = request.query_params.get('building_id')

        # nie pozwalamy mieszac filtrow
        if flat_id_param is not None and building_id_param is not None:
            return Response(
                {"error": "Use either flat_id or building_id, not both."},
                status=status.HTTP_400_BAD_REQUEST
            )

        base_qs = Report.objects.filter(UserId=user)

        # filtr po flat_id
        if flat_id_param is not None:
            try:
                flat_id_int = int(flat_id_param)
            except ValueError:
                return Response(
                    {"flat_id": ["flat_id must be an integer."]},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # autoryzacja czy user ma aktywne przypisanie do tego lokalu
            has_access = UserFlat.objects.filter(
                UserId=user,
                FlatId_id=flat_id_int,
                UserFlatDateTo__isnull=True
            ).exists()
            if not has_access:
                return Response(
                    {"error": "You are not assigned to this flat."},
                    status=status.HTTP_403_FORBIDDEN
                )

            reports = base_qs.filter(FlatId_id=flat_id_int).order_by('-ReportTime')
            serializer = ReportSerializer(reports, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # filtr po building_id
        if building_id_param is not None:
            try:
                building_id_int = int(building_id_param)
            except ValueError:
                return Response(
                    {"building_id": ["building_id must be an integer."]},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # autoryzacja czy user ma jakikolwiek aktywny lokal w tym budynku
            has_access = UserFlat.objects.filter(
                UserId=user,
                FlatId__BuildingId_id=building_id_int,
                UserFlatDateTo__isnull=True
            ).exists()
            if not has_access:
                return Response(
                    {"error": "You have no flat in this building."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # moje BUILDING w tym budynku 
            reports = base_qs.filter(
                ReportType='BUILDING',
                BuildingId_id=building_id_int
            ).order_by('-ReportTime')

            serializer = ReportSerializer(reports, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # brak filtrów czyli wszystkie moje (w tym GENERAL)
        reports = base_qs.order_by('-ReportTime')
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data.copy()
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

            data.pop('FlatId', None)

        elif report_type == 'GENERAL':
            data.pop('FlatId', None)
            data.pop('BuildingId', None)

        else:
            errors['ReportType'] = ['Invalid ReportType. Use FLAT, BUILDING or GENERAL.']

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReportSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)