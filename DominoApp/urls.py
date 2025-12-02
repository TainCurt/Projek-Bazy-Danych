from urllib.parse import urlparse
from django.urls import path
from DominoApp.views import flat, user, building

urlpatterns=[
    path('users/', user.get_users),
    path('users/<int:pk>/', user.user_detail),
    path('buildings/', building.get_buildings),
    path('buildings/<int:pk>/', building.building_detail),
    path('buildings/<int:pk>/', building.building_detail),
    path('buildings/<int:pk>/flats/', flat.building_flats),
    path('buildings/<int:pk>/flats<int:FlatId>/', flat.building_flat_detail)

]