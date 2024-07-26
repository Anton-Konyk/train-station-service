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
    Station
)
from station.serializers import (
    CrewSerializer,
    TrainTypeSerializer,
    TrainTypeImageSerializer,
    TrainListSerializer,
    TrainRetrieveSerializer,
    FacilitySerializer,
    StationSerializer
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

    # def get_serializer_class(self):
    #     if self.action == "list":
    #         return BusListSerializer
    #     elif self.action == "retrieve":
    #         return BusRetrieveSerializer
    #     # elif self.action == "upload_image":
    #     #     return BusImageSerializer
    #     return super().get_serializer_class()  #BusSerializer

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
            queryset = Train.objects.filter(facilities__id__in=facilities_ids).distinct()

        if self.action == ("list", "retrieve"):
            queryset = Train.objects.prefetch_related("facilities")

        return queryset

    # @extend_schema(
    #     parameters=[
    #         OpenApiParameter(
    #             "facilities",
    #             type={"type": "array", "items": {"type": "number"}},
    #             description="Filter by facility id ex. ?facilities=2,3",
    #
    #         ),
    #     ]
    # )

    def list(self, request, *args, **kwargs):
        """Get list of trains."""
        return super().list(request, *args, **kwargs)


class StationResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    pagination_class = StationResultsSetPagination

