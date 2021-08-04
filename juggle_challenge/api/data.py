from dataclasses import dataclass

from django.utils.translation import ugettext_lazy as _


class AvailabilityType:
    ONE_TWO_DAYS_WEEK = _("1-2 days/wk")
    THREE_FOUR_DAYS_WEEK = _("3-4 days/wk")
    FULL_TIME = _("Full Time")


class LocationType:
    ONSITE = _("onsite")
    REMOTE = _("remote")
    MIXED = _("mixed")


@dataclass
class Availability:
    availability_id: str
    description: str


@dataclass
class Location:
    location_id: str
    description: str


AVAILABILITIES = [
    Availability(availability_id="1",
                 description=AvailabilityType.ONE_TWO_DAYS_WEEK),
    Availability(availability_id="2",
                 description=AvailabilityType.THREE_FOUR_DAYS_WEEK),
    Availability(availability_id="3", description=AvailabilityType.FULL_TIME)
]

LOCATIONS = [
    Location(location_id="1",
             description=LocationType.ONSITE),
    Location(location_id="2",
             description=LocationType.REMOTE),
    Location(location_id="3", description=LocationType.MIXED)
]
