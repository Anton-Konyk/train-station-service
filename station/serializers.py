from django.db import transaction
from rest_framework import serializers

from station.models import (
    Crew,
    TrainType,
    Train,
    Facility,
    Station,
    Route,
    Journey,
    Ticket,
    Order,
)


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class FacilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Facility
        fields = ("id", "name")


class TrainTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainType
        fields = ("id", "name", "image")


class TrainTypeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "image")


class TrainSerializer(serializers.ModelSerializer):

    class Meta:
        model = Train
        fields = (
            "id",
            "number",
            "cargo_num",
            "places_in_cargo",
            "num_seats",
            "train_type",
            "facilities"
        )


class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        read_only=True,
        many=False,
        slug_field="name"
    )
    facilities = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )


class TrainRetrieveSerializer(TrainSerializer):
    train_type = TrainTypeSerializer(many=False)
    facilities = FacilitySerializer(many=True)


class StationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        read_only=True,
        many=False,
        slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        read_only=True,
        many=False,
        slug_field="name"
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class JourneySerializer(serializers.ModelSerializer):

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "crews",
            "departure_time",
            "arrival_time"
        )


class JourneyListSerializer(serializers.ModelSerializer):
    train_type_name = serializers.CharField(source="train.train_type.name", read_only=True)
    train_type_image = serializers.CharField(source="train.train_type.image", read_only=True)
    train_facilities = serializers.SlugRelatedField(
        source="train.facilities",
        read_only=True,
        many=True,
        slug_field="name"
    )
    train_num_seats = serializers.IntegerField(
        source="train.num_seats",
        read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "departure_time",
            "arrival_time",
            "train_type_name",
            "train_type_image",
            "train_facilities",
            "train_num_seats",
            "tickets_available"
        )


class JourneyRetrieveSerializer(JourneySerializer):
    route = RouteSerializer(many=False, read_only=True)
    train = TrainRetrieveSerializer(many=False, read_only=True)
    crew = serializers.StringRelatedField(
        many=True,
        read_only=True,
        source="crews"
    )
    taken_seats = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="seat",
        source="tickets"
    )

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "crew",
            "departure_time",
            "arrival_time",
            "taken_seats"
        )


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_ticket(
            attrs["cargo"],
            attrs["seat"],
            attrs["journey"].train,
            serializers.ValidationError
        )
        return data


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            ticket_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in ticket_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class TicketListSerializer(TicketSerializer):
    journey = JourneyListSerializer(read_only=True)


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
