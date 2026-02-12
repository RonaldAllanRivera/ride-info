from datetime import timedelta

from django.db.models import F, FloatField, Prefetch, Value
from django.db.models import Func
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from api.filters import RideFilter
from api.pagination import StandardResultsSetPagination
from api.permissions import IsAdminRole
from api.serializers import RideEventSerializer, RideListSerializer, RideSerializer, UserSerializer
from rides.models import Ride, RideEvent, User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id_user")
    serializer_class = UserSerializer
    permission_classes = (IsAdminRole,)


class RideViewSet(viewsets.ModelViewSet):
    serializer_class = RideSerializer
    permission_classes = (IsAdminRole,)
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RideFilter

    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return RideListSerializer
        return RideSerializer

    def get_queryset(self):
        qs = Ride.objects.select_related("id_rider", "id_driver").all()

        since = timezone.now() - timedelta(hours=24)
        todays_events_qs = (
            RideEvent.objects.filter(created_at__gte=since)
            .only("id_ride_event", "id_ride", "description", "created_at")
            .order_by("-created_at")
        )
        qs = qs.prefetch_related(
            Prefetch("ride_events", queryset=todays_events_qs, to_attr="todays_ride_events")
        )

        ordering = self.request.query_params.get("ordering")
        lat = self.request.query_params.get("lat")
        lon = self.request.query_params.get("lon")

        if lat is not None and lon is not None:
            try:
                lat_f = float(lat)
                lon_f = float(lon)
            except ValueError as exc:
                raise ValidationError({"lat": "Must be a number", "lon": "Must be a number"}) from exc

            pickup_earth = Func(F("pickup_latitude"), F("pickup_longitude"), function="ll_to_earth")
            input_earth = Func(Value(lat_f), Value(lon_f), function="ll_to_earth")
            distance = Func(pickup_earth, input_earth, function="earth_distance", output_field=FloatField())
            qs = qs.annotate(distance_to_pickup_meters=distance)
        else:
            qs = qs.annotate(distance_to_pickup_meters=Value(None, output_field=FloatField()))

        if ordering in {"pickup_time", "-pickup_time"}:
            qs = qs.order_by(ordering, "id_ride")
        elif ordering in {"distance", "-distance"}:
            if lat is None or lon is None:
                raise ValidationError({"ordering": "Distance ordering requires lat and lon query params"})
            direction = "-" if ordering.startswith("-") else ""
            qs = qs.order_by(f"{direction}distance_to_pickup_meters", "id_ride")
        else:
            qs = qs.order_by("id_ride")

        return qs


class RideEventViewSet(viewsets.ModelViewSet):
    queryset = RideEvent.objects.select_related("id_ride").all().order_by("id_ride_event")
    serializer_class = RideEventSerializer
    permission_classes = (IsAdminRole,)
