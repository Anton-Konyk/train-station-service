from django.urls import path, include
from rest_framework import routers

from station.views import (
    CrewViewSet,
    FacilityViewSet,
    TrainTypeViewSet,
    TrainViewSet,
    StationViewSet,
    RouteViewSet,
)

app_name = "station"

router = routers.DefaultRouter()
router.register("crews", CrewViewSet)
router.register("facilities", FacilityViewSet)
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainViewSet)
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)

urlpatterns = [
    path("", include(router.urls))
]
