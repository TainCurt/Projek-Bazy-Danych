from urllib.parse import urlparse
from django.urls import path
from DominoApp.views import announ, flat, user, building, userflat, rent, report

urlpatterns=[
    path('users/', user.get_users),
    path('users/<int:pk>/', user.user_detail),
    path('announ/', announ.get_announ),
    path('announ/<int:pk>/', announ.announ_detail),
    path('reports/', report.get_reports),
    path('reports/<int:pk>/', report.reports_detail),
    path('buildings/', building.get_buildings),
    path('buildings/<int:pk>/', building.building_detail),
    path('buildings/<int:building_id>/flats/', flat.building_flats),
    path('buildings/<int:building_id>/flats/<int:flat_id>/', flat.flat_detail),
    path('buildings/<int:building_id>/flats/<int:flat_id>/rent/', rent.flat_rent),
    path('buildings/<int:building_id>/flats/<int:flat_id>/rent/<int:rent_id>/', rent.falt_rent_detail),
    path('buildings/<int:building_id>/flats/<int:flat_id>/tenants/', userflat.userflat_list),
    path('buildings/<int:building_id>/flats/<int:flat_id>/tenants/<int:userflat_id>/', userflat.userflat_detail)

]