from django.urls import path, include
from rest_framework import routers

from station.views import CrewViewSet

app_name = "station"

router = routers.DefaultRouter()
router.register("crews", CrewViewSet)


urlpatterns = [
    path("", include(router.urls))
]
