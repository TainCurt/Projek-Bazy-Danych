from urllib.parse import urlparse
from django.urls import path
from DominoApp import views

urlpatterns=[
    path('users/', views.get_users)
]