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


class RideListSerializer(serializers.ModelSerializer):
    id_rider = serializers.IntegerField(source="id_rider_id", read_only=True)
    id_driver = serializers.IntegerField(source="id_driver_id", read_only=True)
    rider = UserSerializer(source="id_rider", read_only=True)
    driver = UserSerializer(source="id_driver", read_only=True)
    todays_ride_events = RideEventSerializer(many=True, read_only=True)
    distance_to_pickup_meters = serializers.FloatField(read_only=True, allow_null=True)

    class Meta:
        model = Ride
        fields = (
            "id_ride",
            "status",
            "id_rider",
            "id_driver",
            "rider",
            "driver",
            "pickup_latitude",
            "pickup_longitude",
            "dropoff_latitude",
            "dropoff_longitude",
            "pickup_time",
            "todays_ride_events",
            "distance_to_pickup_meters",
        )
        read_only_fields = fields
