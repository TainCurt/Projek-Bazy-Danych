from django.db.models import Sum, Q, Prefetch
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Flat, RentStatus, UserFlat, UserFlatRole
from DominoApp.utils import get_authenticated_user

@api_view(['GET'])
def high_arrears_flats(request):
    user, error_response = get_authenticated_user(request, required_role='ADMIN')
    if error_response:
        return error_response

    try:
        threshold = float(request.query_params.get('threshold', 2000))
    except ValueError:
        return Response({"error": "Invalid threshold parameter"}, status=400)

    flats_with_debt = Flat.objects.annotate(
        total_debt=Sum(
            'rents__RentAmount', 
            filter=Q(rents__RentStatus=RentStatus.PENDING)
        )
    ).filter(
        total_debt__gt=threshold
    ).prefetch_related(
        Prefetch(
            'userflats',
            queryset=UserFlat.objects.filter(UserFlatRole=UserFlatRole.OWNER).select_related('UserId'),
            to_attr='owners_list'
        ),
        Prefetch(
            'userflats',
            queryset=UserFlat.objects.filter(UserFlatRole=UserFlatRole.TENANT).select_related('UserId'),
            to_attr='tenants_list'
        )
    ).select_related('BuildingId')

    formatted_data = []
    for flat in flats_with_debt:
        owners_info = [
            f"{uf.UserId.UserName} {uf.UserId.UserSurname} ({uf.UserId.UserEmail})"
            for uf in flat.owners_list
        ]

        tenants_info = [
            f"{uf.UserId.UserName} {uf.UserId.UserSurname} ({uf.UserId.UserEmail})"
            for uf in flat.tenants_list
        ]

        formatted_data.append({
            "flat_id": flat.FlatId,
            "flat_number": flat.FlatNumber,
            "building_address": f"{flat.BuildingId.BuildingCity}, {flat.BuildingId.BuildingStreet} {flat.BuildingId.BuildingNumber}",
            "total_debt": flat.total_debt,
            "owners": owners_info,
            "tenants": tenants_info
        })

    return Response(formatted_data, status=status.HTTP_200_OK)