from urllib.parse import urlparse
from django.urls import path
from DominoApp.views import announ, flat, user, building, userflat, rent, report, auth, rent_stats, report_stats, flats_rent_stats
from DominoApp.views.frontend import custom_login_view, home, dashboard_view

urlpatterns=[
    path('api/users/', user.get_users),
    path('api/users/<int:pk>/', user.user_detail),
    path('api/announ/', announ.get_announ),
    path('api/announ/<int:pk>/', announ.announ_detail),
    path('api/reports/', report.get_reports),
    path('api/reports/<int:pk>/', report.reports_detail),
    path('api/buildings/', building.get_buildings),
    path('api/buildings/<int:pk>/', building.building_detail),
    path('api/buildings/<int:building_id>/flats/', flat.building_flats),
    path('api/buildings/<int:building_id>/flats/<int:flat_id>/', flat.flat_detail),
    path('api/buildings/<int:building_id>/flats/<int:flat_id>/rent/', rent.flat_rent),
    path('api/buildings/<int:building_id>/flats/<int:flat_id>/rent/<int:rent_id>/', rent.flat_rent_detail),
    path('api/buildings/<int:building_id>/flats/<int:flat_id>/tenants/', userflat.userflat_list),
    path('api/buildings/<int:building_id>/flats/<int:flat_id>/tenants/<int:userflat_id>/', userflat.userflat_detail),
    path('api/login/', auth.login),
    path('api/me/', user.me),
    path('api/my/flats/', user.my_flats),
    path('api/my/rents/', user.my_rents),
    path('api/my/reports/', user.my_reports),
    path('api/rentstats/', rent_stats.arrears_by_building),
    path('api/reportstats/', report_stats.report_statistics),
    path('api/flatsrentstats/', flats_rent_stats.high_arrears_flats),

    path('', home, name='home'),
    path('login/', custom_login_view, name='custom-login'),
    path('dashboard/', dashboard_view, name='dashboard'),
]