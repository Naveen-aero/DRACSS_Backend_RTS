from rest_framework import viewsets, filters
from .models import ReturnToBaseServiceRequest
from .serializers import ReturnToBaseServiceRequestSerializer


class ReturnToBaseServiceRequestViewSet(viewsets.ModelViewSet):
    """
    CRUD:
      GET    /api/rtb-service-requests/
      POST   /api/rtb-service-requests/
      GET    /api/rtb-service-requests/{id}/
      PUT    /api/rtb-service-requests/{id}/
      PATCH  /api/rtb-service-requests/{id}/
      DELETE /api/rtb-service-requests/{id}/
    """

    # ONLY CHANGE: prefetch_related("components") for nested list
    queryset = ReturnToBaseServiceRequest.objects.all().prefetch_related("components")

    serializer_class = ReturnToBaseServiceRequestSerializer

    # Useful filtering/search for admin UI
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = [
        # Base fields
        "uas_model",
        "flight_controller",
        "serial_number",
        "affected_subsystem_component",
        "reported_by",

        #  NEW: Intrack fields
        "intrack_tracking_id",
        "intrack_courier",
        "intrack_status",

        #  NEW: Outtrack fields
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
