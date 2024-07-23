from rest_framework import viewsets

from station.models import Crew
from train_station_service.serializers import CrewSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
