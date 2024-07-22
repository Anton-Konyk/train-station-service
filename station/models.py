import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.conf import settings


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return self.first_name + " " + self.last_name


def movie_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/train/", filename)


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(null=True, upload_to=movie_image_file_path)

    def __str__(self):
        return self.name


class Train(models.Model):
    number = models.IntegerField(unique=True)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.number)

    class Meta:
        ordering = ["number"]


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"

    class Meta:
        ordering = ["name"]


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="route_from")
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="route_to")
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source.name} -> {self.destination.name} ({self.distance} km)"

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination stations cannot be the same.")

    class Meta:
        unique_together = ["source", "destination"]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    crews = models.ManyToManyField(Crew, related_name="journeys")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"{self.route}, train: {self.train}, departure: {self.departure_time}"


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(
        Journey, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    # @staticmethod
    # def validate_ticket(row, seat, cinema_hall, error_to_raise):
    #     for ticket_attr_value, ticket_attr_name, cinema_hall_attr_name in [
    #         (row, "row", "rows"),
    #         (seat, "seat", "seats_in_row"),
    #     ]:
    #         count_attrs = getattr(cinema_hall, cinema_hall_attr_name)
    #         if not (1 <= ticket_attr_value <= count_attrs):
    #             raise error_to_raise(
    #                 {
    #                     ticket_attr_name: f"{ticket_attr_name} "
    #                     f"number must be in available range: "
    #                     f"(1, {cinema_hall_attr_name}): "
    #                     f"(1, {count_attrs})"
    #                 }
    #             )
    #
    # def clean(self):
    #     Ticket.validate_ticket(
    #         self.row,
    #         self.seat,
    #         self.movie_session.cinema_hall,
    #         ValidationError,
    #     )
    #
    # def save(
    #     self,
    #     force_insert=False,
    #     force_update=False,
    #     using=None,
    #     update_fields=None,
    # ):
    #     self.full_clean()
    #     return super(Ticket, self).save(
    #         force_insert, force_update, using, update_fields
    #     )

    def __str__(self):
        return (
            f"{str(self.journey)} (cargo: {self.cargo}, seat: {self.seat})"
        )

    class Meta:
        unique_together = ("journey", "cargo", "seat")
        ordering = ["cargo", "seat"]
