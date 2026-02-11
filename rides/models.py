from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from rides.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_ADMIN = "admin"
    ROLE_USER = "user"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "admin"),
        (ROLE_USER, "user"),
    ]

    id_user = models.BigAutoField(primary_key=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default=ROLE_USER)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=50, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        return self.email

    @property
    def id(self):
        return self.id_user


class Ride(models.Model):
    id_ride = models.BigAutoField(primary_key=True)
    status = models.CharField(max_length=50, db_index=True)

    id_rider = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="rides_as_rider",
        db_column="id_rider",
    )
    id_driver = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="rides_as_driver",
        db_column="id_driver",
    )

    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField(db_index=True)

    def __str__(self) -> str:
        return f"Ride {self.id_ride}"


class RideEvent(models.Model):
    id_ride_event = models.BigAutoField(primary_key=True)
    id_ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name="ride_events",
        db_column="id_ride",
    )
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(db_index=True)

    def __str__(self) -> str:
        return f"RideEvent {self.id_ride_event}"
