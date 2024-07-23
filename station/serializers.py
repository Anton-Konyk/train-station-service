from rest_framework import serializers

from station.models import Crew


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ("first_name", "last_name")

