from __future__ import annotations

from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.hashers import make_password
from django.db import transaction

from rest_framework import serializers

from .models import Job, Professional, Business


class AuthUserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        with transaction.atomic():
            validated_data["password"] = make_password(validated_data["password"])
            instance = super().create(validated_data)

            return instance

    class Meta:
        model = AuthUser
        fields = ["first_name", "last_name", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ("business_id", "company_name", "website")
        read_only_fields = ["business_id"]


class AvailabilitySerializer(serializers.Serializer):
    availability_id = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)


class LocationSerializer(serializers.Serializer):
    location_id = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)


class JobSerializer(serializers.ModelSerializer):
    availabilities = AvailabilitySerializer(read_only=True, many=True)
    locations = LocationSerializer(read_only=True, many=True)

    class Meta:
        model = Job
        fields = (
            "job_id",
            "title",
            "daily_rate_range",
            "availability_ids",
            "location_ids",
            "skills",
            "availabilities",
            "locations",
        )
        read_only_fields = ["job_id"]
        extra_kwargs = {
            "availability_ids": {"write_only": True},
            "location_ids": {"write_only": True},
        }


class ProfessionalSerializer(serializers.ModelSerializer):
    jobs = JobSerializer(read_only=True, many=True)
    availabilities = AvailabilitySerializer(read_only=True, many=True)
    locations = LocationSerializer(read_only=True, many=True)

    class Meta:
        model = Professional
        fields = (
            "professional_id",
            "full_name",
            "email",
            "title",
            "daily_rate_range",
            "availability_ids",
            "location_ids",
            "availabilities",
            "locations",
            "jobs",
        )
        read_only_fields = ["professional_id"]
        extra_kwargs = {
            "availability_ids": {"write_only": True},
            "location_ids": {"write_only": True},
        }
