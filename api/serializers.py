from rest_framework import serializers

from rides.models import Ride, RideEvent, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id_user",
            "role",
            "first_name",
            "last_name",
            "email",
            "phone_number",
        )
        read_only_fields = ("id_user",)


class RideEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideEvent
        fields = (
            "id_ride_event",
            "id_ride",
            "description",
            "created_at",
        )
        read_only_fields = ("id_ride_event",)


class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = (
            "id_ride",
            "status",
            "id_rider",
            "id_driver",
            "pickup_latitude",
            "pickup_longitude",
            "dropoff_latitude",
            "dropoff_longitude",
            "pickup_time",
        )
        read_only_fields = ("id_ride",)
