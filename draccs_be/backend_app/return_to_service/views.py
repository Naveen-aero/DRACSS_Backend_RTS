from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ReturnToBaseServiceRequest, RTBServiceRequestComponent
from .serializers import (
    ReturnToBaseServiceRequestSerializer,
    RTBServiceRequestComponentSerializer,
)


class ReturnToBaseServiceRequestViewSet(viewsets.ModelViewSet):
    """
    CRUD:
      GET    /api/rtb-service-requests/
      POST   /api/rtb-service-requests/
      GET    /api/rtb-service-requests/{id}/
      PUT    /api/rtb-service-requests/{id}/
      PATCH  /api/rtb-service-requests/{id}/
      DELETE /api/rtb-service-requests/{id}/

    NEW (nested component endpoint):
      GET    /api/rtb-service-requests/{id}/component/{component_id}/
      PATCH  /api/rtb-service-requests/{id}/component/{component_id}/
    """

    queryset = ReturnToBaseServiceRequest.objects.all().prefetch_related("components")
    serializer_class = ReturnToBaseServiceRequestSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = [
        "uas_model",
        "flight_controller",
        "serial_number",
        "affected_subsystem_component",
        "reported_by",
        "intrack_tracking_id",
        "intrack_courier",
        "intrack_status",
        "outtrack_tracking_id",
        "outtrack_courier",
        "outtrack_status",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "date_of_occurrence",
        "reported_date",
        "intrack_shipping_date",
        "outtrack_shipping_date",
    ]

    #  /api/rtb-service-requests/<id>/component/<component_id>/
    @action(
        detail=True,
        methods=["get", "patch"],
        url_path=r"component/(?P<component_id>[^/.]+)",
        serializer_class=RTBServiceRequestComponentSerializer,  #  IMPORTANT FIX
    )
    def component_detail(self, request, pk=None, component_id=None):
        rtb = self.get_object()

        try:
            comp = rtb.components.get(id=component_id)
        except RTBServiceRequestComponent.DoesNotExist:
            return Response(
                {"detail": "Component not found for this RTB request."},
                status=status.HTTP_404_NOT_FOUND,
            )

        #  GET one component
        if request.method.lower() == "get":
            serializer = self.get_serializer(comp)  #  uses action serializer
            return Response(serializer.data, status=status.HTTP_200_OK)

        #  PATCH one component
        serializer = self.get_serializer(comp, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)