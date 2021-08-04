"""api models"""
from __future__ import annotations

from typing import List

from django.db import models
from django.core import validators
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model

from .data import AVAILABILITIES, LOCATIONS, Availability

from juggle_challenge import utils


User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(default=utils.now_with_tz)
    updated_at = models.DateTimeField(default=utils.now_with_tz)

    class Meta:
        abstract = True

    def __str__(self):
        return "{}(id={!r})".format(self.__class__.__name__, self.pk)

    def save(self, *args, **kwargs):
        self.updated_at = utils.now_with_tz()
        super().save(*args, **kwargs)


class Business(BaseModel):
    class Meta:
        db_table = "business"

    company_name = models.CharField(max_length=255)
    website = models.URLField()

    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    @property
    def business_id(self):
        return self.pk


class Job(BaseModel):
    class Meta:
        db_table = "job"

    title = models.CharField(max_length=50)
    daily_rate_range = models.DecimalField(max_digits=20, decimal_places=3)
    availability_ids = ArrayField(models.CharField(max_length=10))
    location_ids = ArrayField(models.CharField(max_length=10))
    skills = ArrayField(models.CharField(max_length=50))

    business = models.ForeignKey("Business", on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    @property
    def job_id(self):
        return self.pk

    @property
    def availabilities(self) -> List[Availability]:
        return list(
            utils.filter_items(self.availability_ids, "availability_id", AVAILABILITIES)
        )

    @property
    def locations(self) -> List[Availability]:
        return list(utils.filter_items(self.location_ids, "location_id", LOCATIONS))

    def __unicode__(self):
        return self.name


class Professional(BaseModel):
    class Meta:
        db_table = "professional"

    full_name = models.CharField(max_length=255)
    email = models.CharField(
        max_length=254,
        validators=[validators.validate_email],
        help_text="Email address of the professional",
    )
    title = models.CharField(max_length=50)
    daily_rate_range = models.DecimalField(max_digits=20, decimal_places=3)
    availability_ids = ArrayField(models.CharField(max_length=10))
    location_ids = ArrayField(models.CharField(max_length=10))

    jobs = models.ManyToManyField(
        Job, related_name="professional_list", blank=True, through="Application"
    )
    owner = models.ForeignKey(User, on_delete=models.PROTECT)

    @property
    def professional_id(self):
        return self.pk

    @property
    def availabilities(self) -> List[Availability]:
        return list(
            utils.filter_items(self.availability_ids, "availability_id", AVAILABILITIES)
        )

    @property
    def locations(self) -> List[Availability]:
        return list(utils.filter_items(self.location_ids, "location_id", LOCATIONS))


class Application(BaseModel):
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
