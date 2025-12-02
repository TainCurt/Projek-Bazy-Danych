from dataclasses import field
from unittest import mock
from rest_framework import serializers
from .models import User, Building, Flat, UserFlat, Rent, Report, Announ



class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class FlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flat
        fields = '__all__'


class UserFlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFlat
        fields = '__all__'


class RentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rent
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'


class AnnounSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announ
        fields = '__all__'

