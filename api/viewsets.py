from rest_framework import viewsets

from api.permissions import IsAdminRole
from api.serializers import RideEventSerializer, RideSerializer, UserSerializer
from rides.models import Ride, RideEvent, User


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id_user")
    serializer_class = UserSerializer
    permission_classes = (IsAdminRole,)


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.select_related("id_rider", "id_driver").all().order_by("id_ride")
    serializer_class = RideSerializer
    permission_classes = (IsAdminRole,)


class RideEventViewSet(viewsets.ModelViewSet):
    queryset = RideEvent.objects.select_related("id_ride").all().order_by("id_ride_event")
    serializer_class = RideEventSerializer
    permission_classes = (IsAdminRole,)
