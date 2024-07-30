from django.db.models import Count, F
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

from station.models import (
    Crew,
    TrainType,
    Train,
    Facility,
    Station,
    Route,
    Journey, Order,
)
from station.serializers import (
    CrewSerializer,
    TrainTypeSerializer,
    TrainTypeImageSerializer,
    TrainListSerializer,
    TrainRetrieveSerializer,
    FacilitySerializer,
    StationSerializer,
    RouteSerializer,
    JourneyListSerializer,
    JourneyRetrieveSerializer,
    JourneySerializer, OrderSerializer, OrderListSerializer,
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer


class TrainTypeViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAdminUser],
        url_path="upload-image",
        serializer_class=TrainTypeImageSerializer,
    )
    def upload_image(self, request, pk=None):
        train_type = self.get_object()
        serializer = self.get_serializer(train_type, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrainResultsSetPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = "page_size"
    max_page_size = 100


class TrainViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Train.objects.all()
    serializer_class = TrainListSerializer
    pagination_class = TrainResultsSetPagination

    @staticmethod
    def _params_to_ints(query_string):
        """Converts a string of format '1,2,3' to a list of integers [1,2,3]"""
        return [int(str_id) for str_id in query_string.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        elif self.action == "retrieve":
            return TrainRetrieveSerializer
        return super().get_serializer_class()  #TrainSerializer

    def get_queryset(self):
        queryset = self.queryset
        facilities = self.request.query_params.get("facilities")
        if facilities:
            facilities_ids = self._params_to_ints(facilities)
            queryset = (
                Train.objects.filter(
                    facilities__id__in=facilities_ids
                ).distinct())

        if self.action == ("list", "retrieve"):
            queryset = Train.objects.prefetch_related("facilities")

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "facilities",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by facility id ex. ?facilities=2,3",

            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of trains with facilities."""
        return super().list(request, *args, **kwargs)


class StationResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    pagination_class = StationResultsSetPagination


class RouteResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class RouteViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    pagination_class = RouteResultsSetPagination

    def get_queryset(self):
        queryset = self.queryset
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        if source:
            source_ids = (Station.objects.filter(name__icontains=source).
                          values_list("id"))
            queryset = Route.objects.filter(source__id__in=source_ids)
        if destination:
            destination_ids = Station.objects.filter(
                name__icontains=destination).values_list("id")
            queryset = (
                Route.objects.filter(destination__id__in=destination_ids))

        if self.action == ("list", "retrieve"):
            queryset = Route.objects.prefetch_related("source")

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type={"type": "string", "items": {"type": "name"}},
                description="Filter by source station id ex. ?source=Berlin",

            ),
            OpenApiParameter(
                "destination",
                type={"type": "string", "items": {"type": "name"}},
                description="Filter by destination station id ex. ?destination=Vien",

            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of routes."""
        return super().list(request, *args, **kwargs)


class JourneyResultsSetPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = "page_size"
    max_page_size = 100


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    pagination_class = JourneyResultsSetPagination

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        elif self.action == "retrieve":
            return JourneyRetrieveSerializer
        return JourneySerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = (
                queryset
                .select_related("train")
                .annotate(
                    tickets_available=(
                     F("train__cargo_num") * F("train__places_in_cargo")
                     - Count("tickets"))
                )
            )
        elif self.action == "retrieve":
            queryset = queryset.prefetch_related("crews")
        return queryset.order_by("id")


class OrderResultsSetPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = "page_size"
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderResultsSetPagination

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related("tickets__journey__train")
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == "list":
            serializer = OrderListSerializer
        return serializer
