from dataclasses import field
from unittest import mock
from rest_framework import serializers
from .models import User, Building, Flat, UserFlat, Rent, Report, Announ



class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = '__all__'


class UserFlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFlat
        fields = '__all__'


class FlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flat
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    Flats = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Flat.objects.all()
    )

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        flats = validated_data.pop('Flats', [])
        user = User.objects.create(**validated_data)

        for flat in flats:
            UserFlat.objects.create(UserId=user, FlatId=flat)

        return user

    def update(self, instance, validated_data):
        flats = validated_data.pop('Flats', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        if flats is not None:
            UserFlat.objects.filter(UserId=instance).delete()
            for flat in flats:
                UserFlat.objects.create(UserId=instance, FlatId=flat)

        return instance



class RentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rent
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):
    UserId = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    FlatId = serializers.PrimaryKeyRelatedField(queryset=Flat.objects.all())
    BuildingId = serializers.PrimaryKeyRelatedField(queryset=Building.objects.all())
    class Meta:
        model = Report
        fields = '__all__'


class AnnounSerializer(serializers.ModelSerializer):
    UserId = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Announ
        fields = '__all__'

