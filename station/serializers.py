from rest_framework import serializers

from station.models import Crew, TrainType


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class TrainTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainTypeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "image")
