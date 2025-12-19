from math import fabs
import stat
from django.shortcuts import render
from django.urls import is_valid_path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Report
from ..serializer import ReportSerializer
from DominoApp import serializer
from DominoApp.utils import get_authenticated_user

@api_view(['GET', 'POST'])
def get_reports(request):
    user, error_response = get_authenticated_user(request, required_role='ADMIN')
    if error_response:
        return error_response
    
    if request.method == 'GET':
        reports = Report.objects.all()

        # filtr po statusie
        status_param = request.query_params.get('status')
        if status_param:
            status_param = status_param.upper()
            allowed_statuses = ['WAITING', 'DONE', 'ABANDONED']
            if status_param not in allowed_statuses:
                return Response(
                    {'status': ['Invalid status. Use WAITING, DONE or ABANDONED.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            reports = reports.filter(ReportStatus=status_param)

        # filtr po budynku
        building_id_param = request.query_params.get('building_id')
        if building_id_param:
            try:
                building_id_int = int(building_id_param)
            except ValueError:
                return Response(
                    {'building_id': ['building_id must be an integer.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            reports = reports.filter(BuildingId_id=building_id_int)

        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def reports_detail(request, pk):
    user, error_response = get_authenticated_user(request, required_role='ADMIN')
    if error_response:
        return error_response
    
    try:
        report = Report.objects.get(pk=pk)
    except Report.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ReportSerializer(report)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Admin moze zmieniac TYLKO status zgloszenia
        new_status = request.data.get('ReportStatus')
        if new_status:
            new_status = new_status.upper()

        if not new_status:
            return Response(
                {'ReportStatus': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        allowed_statuses = ['WAITING', 'DONE', 'ABANDONED']
        if new_status not in allowed_statuses:
            return Response(
                {'ReportStatus': ['Invalid status. Use WAITING, DONE or ABANDONED.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        report.ReportStatus = new_status
        report.save()

        serializer = ReportSerializer(report)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
