from __future__ import annotations

import datetime

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, DateTimeFilter, CharFilter

from rest_framework import decorators, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny


from .models import Business, Job, Professional
from .serializers import (
    AuthUserSerializer,
    BusinessSerializer,
    JobSerializer,
    ProfessionalSerializer,
)
from juggle_challenge.baseviews import ChildMixin, OwnerSaveMixin

AuthUser = get_user_model()


class CreateUserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (AllowAny,)
    queryset = AuthUser.objects.all()
    serializer_class = AuthUserSerializer


class JobFilterSet(FilterSet):
    title = CharFilter(lookup_expr="iexact")
    daily_date_range = CharFilter(lookup_expr="iexact")
    min_created_datetime = DateTimeFilter(field_name="created_at", lookup_expr="gte")
    max_created_datetime = DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Job
        fields = [
            "title",
            "daily_date_range",
            "min_created_datetime",
            "max_created_datetime",
        ]


class JobViewSet(ChildMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobFilterSet

    def get_professional_serializer_class(self):
        return ProfessionalSerializer

    @decorators.action(detail=True, methods=["get"])
    def professionals(self, request, pk):
        resp = self.child_action(
            request,
            serializer_class=self.get_professional_serializer_class(),
            view_name="professional-detail",
            queryset=self.get_object().professional_list,
            lookup_field="pk",
            parent_name="job",
        )
        return resp


class ProfessionalFilterSet(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    daily_date_range = CharFilter(lookup_expr="iexact")
    email = CharFilter(lookup_expr="iexact")
    full_name = CharFilter(lookup_expr="icontains")
    min_created_datetime = DateTimeFilter(field_name="created_at", lookup_expr="gte")
    max_created_datetime = DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Professional
        fields = [
            "title",
            "daily_date_range",
            "email",
            "full_name",
            "min_created_datetime",
            "max_created_datetime",
        ]


class ProfessionalViewSet(ChildMixin, OwnerSaveMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Professional.objects.all()
    serializer_class = ProfessionalSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProfessionalFilterSet

    def get_job_serializer_class(self):
        return JobSerializer

    @decorators.action(detail=True, methods=["get"])
    def jobs(self, request, pk):
        resp = self.child_action(
            request,
            serializer_class=self.get_job_serializer_class(),
            view_name="job-detail",
            queryset=self.get_object().jobs,
            lookup_field="pk",
            parent_name="professional",
        )
        return resp

    @decorators.action(
        detail=True,
        methods=["put"],
        url_path="job-apply/(?P<job_id>[^/.]+)",
        url_name="job-apply",
    )
    def job_apply(self, request, job_id, pk):
        with transaction.atomic():
            professional = self.get_object()
            job = get_object_or_404(Job, pk=job_id)

            if (
                job.professional_list.filter(
                    created_at__date=datetime.date.today()
                ).count()
                >= 5
            ):
                raise ValidationError(
                    "The limit of applications for the current job was reached. Please try again tomorrow."
                )

            professional.jobs.add(job)

        return Response(status=status.HTTP_200_OK)


class BusinessCreateViewSet(
    OwnerSaveMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    queryset = Business.objects.order_by("pk").all()
    serializer_class = BusinessSerializer


class BusinessRetrieveUpdateViewSet(
    ChildMixin,
    OwnerSaveMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    queryset = Business.objects.order_by("pk").all()
    serializer_class = BusinessSerializer

    def get_job_serializer_class(self):
        return JobSerializer

    @decorators.action(detail=True, methods=["get", "post"])
    def jobs(self, request, pk):
        resp = self.child_action(
            request,
            serializer_class=self.get_job_serializer_class(),
            view_name="job-detail",
            queryset=self.get_object().job_set,
            lookup_field="pk",
            parent_name="business",
        )
        return resp
