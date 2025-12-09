from dataclasses import field
from unittest import mock
from rest_framework import serializers
from .models import User, Building, Flat, UserFlat, Rent, Report, Announ, UserRole
from django.contrib.auth.hashers import make_password




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
        queryset=Flat.objects.all(),
        required=False
    )

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'UserPassword' : {'write_only': True},
            'UserRole' : {"required": False}
        }

    def create(self, validated_data):
        flats = validated_data.pop('Flats', [])

        role = validated_data.get("UserRole")
        if not role:
            validated_data["UserRole"] = UserRole.RESIDENT

        password = validated_data.get("UserPassword")
        if password:
            validated_data["UserPassword"] = make_password(password)

        user = User.objects.create(**validated_data)

        for flat in flats:
            UserFlat.objects.create(
                UserId=user,
                FlatId=flat,
                UserFlatRole='TENANT'
            )

        return user

    def update(self, instance, validated_data):
        flats = validated_data.pop('Flats', None)
        password = validated_data.get("UserPassword")

        if password:
            validated_data["UserPassword"] = make_password(password)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        if flats is not None:
            UserFlat.objects.filter(UserId=instance).delete()
            for flat in flats:
                UserFlat.objects.create(
                    UserId=instance,
                    FlatId=flat,
                    UserFlatRole='TENANT'
                )

        return instance



class RentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rent
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):
    UserId = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    FlatId = serializers.PrimaryKeyRelatedField(
        queryset=Flat.objects.all(),
        required=False,
        allow_null=True
    )
    BuildingId = serializers.PrimaryKeyRelatedField(
        queryset=Building.objects.all(),
        required=False,
        allow_null=True
    )
    class Meta:
        model = Report
        fields = '__all__'


class AnnounSerializer(serializers.ModelSerializer):
    UserId = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Announ
        fields = '__all__'

