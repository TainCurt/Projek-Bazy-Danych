from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Report
from DominoApp.utils import get_authenticated_user

@api_view(['GET'])
def report_statistics(request):
    user, error_response = get_authenticated_user(request, required_role='ADMIN')
    if error_response:
        return error_response

    stats = Report.objects.filter(ReportType='BUILDING').values(
        'BuildingId__BuildingCity',
        'BuildingId__BuildingStreet',
        'BuildingId__BuildingNumber',
        'ReportStatus'
    ).annotate(
        count=Count('ReportId')
    ).order_by('BuildingId__BuildingCity', 'BuildingId__BuildingStreet', 'ReportStatus')

    formatted_data = []
    for entry in stats:
        city = entry['BuildingId__BuildingCity'] or ""
        street = entry['BuildingId__BuildingStreet'] or ""
        number = entry['BuildingId__BuildingNumber'] or ""
        
        building_str = f"{city}, {street} {number}".strip()
        if not building_str or building_str == ",":
            building_str = "Nieprzypisany budynek"

        formatted_data.append({
            "building": building_str,
            "status": entry['ReportStatus'],
            "count": entry['count']
        })

    return Response(formatted_data, status=status.HTTP_200_OK)