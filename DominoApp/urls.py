from urllib.parse import urlparse
from django.urls import path
from DominoApp.views import announ, flat, user, building, userflat, rent, report, auth, rent_stats, report_stats, flats_rent_stats
from DominoApp.views.frontend import custom_login_view, home, dashboard_view, buildings_list_view, building_details_view, flat_details_view, profile_view, announcements_view, my_flats_view, my_rents_view, my_reports_view, admin_reports_view, admin_users_view

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
    path('profile/', profile_view, name='profile'),
    path('announcements/', announcements_view, name='announcements'),
    path('my/flats/', my_flats_view, name='my-flats'),
    path('my/rents/', my_rents_view, name='my-rents'),
    path('my/reports/', my_reports_view, name='my-reports'),
    path('reports/admin/', admin_reports_view, name='admin-reports'),
    path('users/admin/', admin_users_view, name='admin-users'),
    path('buildings/', buildings_list_view, name='buildings-list'),
    path('buildings/<int:building_id>/', building_details_view, name='building-details'),
    path('buildings/<int:building_id>/flats/<int:flat_id>/', flat_details_view, name='flat-details'),
]