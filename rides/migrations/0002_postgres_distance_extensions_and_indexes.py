from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rides", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "CREATE EXTENSION IF NOT EXISTS cube;",
                "CREATE EXTENSION IF NOT EXISTS earthdistance;",
            ],
            reverse_sql=[
                "DROP EXTENSION IF EXISTS earthdistance;",
                "DROP EXTENSION IF EXISTS cube;",
            ],
        ),
        migrations.RunSQL(
            sql=[
                "CREATE INDEX IF NOT EXISTS rides_ride_id_rider_idx ON rides_ride (id_rider);",
                "CREATE INDEX IF NOT EXISTS rides_ride_id_driver_idx ON rides_ride (id_driver);",
                "CREATE INDEX IF NOT EXISTS rides_rideevent_ride_created_idx ON rides_rideevent (id_ride, created_at DESC);",
                "CREATE INDEX IF NOT EXISTS rides_ride_pickup_earth_idx ON rides_ride USING gist (ll_to_earth(pickup_latitude, pickup_longitude));",
            ],
            reverse_sql=[
                "DROP INDEX IF EXISTS rides_ride_pickup_earth_idx;",
                "DROP INDEX IF EXISTS rides_rideevent_ride_created_idx;",
                "DROP INDEX IF EXISTS rides_ride_id_driver_idx;",
                "DROP INDEX IF EXISTS rides_ride_id_rider_idx;",
            ],
        ),
    ]
