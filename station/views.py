from rest_framework import viewsets

from station.models import Crew
from station.serializers import CrewSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
