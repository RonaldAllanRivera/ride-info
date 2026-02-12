from __future__ import annotations

import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from rides.models import Ride, RideEvent


class Command(BaseCommand):
    help = "Seed the local database with sample Users, Rides, and RideEvents."

    def add_arguments(self, parser):
        parser.add_argument("--rides", type=int, default=25)
        parser.add_argument("--events-per-ride", type=int, default=4)
        parser.add_argument("--drivers", type=int, default=5)
        parser.add_argument("--riders", type=int, default=10)
        parser.add_argument("--seed", type=int, default=1337)
        parser.add_argument("--center-lat", type=float, default=14.5995)
        parser.add_argument("--center-lon", type=float, default=120.9842)
        parser.add_argument(
            "--force",
            action="store_true",
            help="Create additional sample data even if rides already exist.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        ride_count = int(options["rides"])
        events_per_ride = int(options["events_per_ride"])
        drivers_count = int(options["drivers"])
        riders_count = int(options["riders"])
        seed = int(options["seed"])
        center_lat = float(options["center_lat"])
        center_lon = float(options["center_lon"])
        force = bool(options["force"])

        if ride_count <= 0:
            self.stdout.write(self.style.WARNING("No rides requested; nothing to do."))
            return

        if Ride.objects.exists() and not force:
            self.stdout.write(
                self.style.WARNING(
                    "Rides already exist. Re-run with --force to add more sample data."
                )
            )
            return

        rng = random.Random(seed)
        User = get_user_model()

        def make_email(prefix: str, i: int) -> str:
            return f"{prefix}{i}@example.com"

        def ensure_user(email: str, role: str) -> object:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "role": role,
                    "first_name": prefix_title(role),
                    "last_name": str(email.split("@")[0]),
                    "is_staff": role == "admin",
                },
            )
            if created:
                user.set_password("password")
                user.save(update_fields=["password"])
            return user

        def prefix_title(role: str) -> str:
            if role == "admin":
                return "Admin"
            if role == "user":
                return "User"
            return "Person"

        drivers = [ensure_user(make_email("driver", i + 1), "user") for i in range(drivers_count)]
        riders = [ensure_user(make_email("rider", i + 1), "user") for i in range(riders_count)]

        statuses = ["en-route", "pickup", "dropoff"]
        now = timezone.now()

        created_rides = []
        created_events = 0

        for i in range(ride_count):
            pickup_lat = center_lat + rng.uniform(-0.03, 0.03)
            pickup_lon = center_lon + rng.uniform(-0.03, 0.03)
            dropoff_lat = center_lat + rng.uniform(-0.06, 0.06)
            dropoff_lon = center_lon + rng.uniform(-0.06, 0.06)

            pickup_time = now - timedelta(hours=rng.uniform(0, 72))
            if i == 0:
                pickup_time = now - timedelta(hours=6)
            status = rng.choice(statuses)

            ride = Ride.objects.create(
                status=status,
                id_rider=rng.choice(riders),
                id_driver=rng.choice(drivers),
                pickup_latitude=pickup_lat,
                pickup_longitude=pickup_lon,
                dropoff_latitude=dropoff_lat,
                dropoff_longitude=dropoff_lon,
                pickup_time=pickup_time,
            )
            created_rides.append(ride)

            # Ensure at least one event within last 24 hours to exercise `todays_ride_events`.
            if i == 0:
                pickup_event_at = pickup_time + timedelta(minutes=1)
                dropoff_event_at = pickup_time + timedelta(hours=2, minutes=5)

                if pickup_event_at > now:
                    pickup_event_at = now - timedelta(minutes=10)
                if dropoff_event_at > now:
                    dropoff_event_at = now - timedelta(minutes=1)

                RideEvent.objects.create(
                    id_ride=ride,
                    description="Status changed to pickup",
                    created_at=pickup_event_at,
                )
                created_events += 1

                RideEvent.objects.create(
                    id_ride=ride,
                    description="Status changed to dropoff",
                    created_at=dropoff_event_at,
                )
                created_events += 1
            else:
                RideEvent.objects.create(
                    id_ride=ride,
                    description="Status changed to pickup",
                    created_at=now - timedelta(hours=rng.uniform(0.1, 20)),
                )
                created_events += 1

            for _ in range(max(events_per_ride - 1, 0)):
                age_hours = rng.uniform(0, 120)
                created_at = now - timedelta(hours=age_hours)
                RideEvent.objects.create(
                    id_ride=ride,
                    description=rng.choice(
                        [
                            "Status changed to en-route",
                            "Status changed to pickup",
                            "Status changed to dropoff",
                            "Driver arrived",
                            "Rider picked up",
                            "Rider dropped off",
                        ]
                    ),
                    created_at=created_at,
                )
                created_events += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: rides={len(created_rides)} ride_events={created_events} "
                f"drivers={len(drivers)} riders={len(riders)}"
            )
        )
