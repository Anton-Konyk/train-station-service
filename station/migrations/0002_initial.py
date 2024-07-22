# Generated by Django 5.0.7 on 2024-07-22 16:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("station", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="journey",
            name="route",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="station.route"
            ),
        ),
        migrations.AddField(
            model_name="route",
            name="destination",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="route_to",
                to="station.station",
            ),
        ),
        migrations.AddField(
            model_name="route",
            name="source",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="route_from",
                to="station.station",
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="journey",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tickets",
                to="station.journey",
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tickets",
                to="station.order",
            ),
        ),
        migrations.AddField(
            model_name="journey",
            name="train",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="station.train"
            ),
        ),
        migrations.AddField(
            model_name="train",
            name="train_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="station.traintype"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="route",
            unique_together={("source", "destination")},
        ),
        migrations.AlterUniqueTogether(
            name="ticket",
            unique_together={("journey", "cargo", "seat")},
        ),
    ]
