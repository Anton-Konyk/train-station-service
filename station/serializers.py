from rest_framework import serializers

from station.models import (
    Crew,
    TrainType,
    Train,
    Facility,
    Station,
    Route
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
            "is_small",
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
