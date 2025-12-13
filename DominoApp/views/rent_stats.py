from datetime import datetime
from django.db.models import Sum, Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Rent, RentStatus
from DominoApp.utils import get_authenticated_user

@api_view(['GET'])
def arrears_by_building(request):
    user, error_response = get_authenticated_user(request, required_role='ADMIN')
    if error_response:
        return error_response

    try:
        now = datetime.now()
        month = int(request.query_params.get('month', now.month))
        year = int(request.query_params.get('year', now.year))
    except ValueError:
        return Response({"error": "Invalid month or year parameters"}, status=400)

    stats = Rent.objects.filter(
        RentMonth=month,
        RentYear=year
    ).values(
        'FlatId__BuildingId__BuildingCity',
        'FlatId__BuildingId__BuildingStreet',
        'FlatId__BuildingId__BuildingNumber'
    ).annotate(
        total_charges=Sum('RentAmount'),
        total_arrears=Sum('RentAmount', filter=Q(RentStatus=RentStatus.PENDING))
    ).order_by('FlatId__BuildingId__BuildingCity', 'FlatId__BuildingId__BuildingStreet')

    formatted_data = []
    for entry in stats:
        total_charges = entry['total_charges'] or 0
        total_arrears = entry['total_arrears'] or 0
        
        city = entry['FlatId__BuildingId__BuildingCity']
        street = entry['FlatId__BuildingId__BuildingStreet']
        number = entry['FlatId__BuildingId__BuildingNumber']

        formatted_data.append({
            "building": f"{city}, {street} {number}",
            "period": f"{month}/{year}",
            "total_charges": total_charges,
            "total_arrears": total_arrears
        })

    return Response(formatted_data, status=status.HTTP_200_OK)