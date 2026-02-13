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
    queryset = ReturnToBaseServiceRequest.objects.all()
    serializer_class = ReturnToBaseServiceRequestSerializer

    # Useful filtering/search for admin UI
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "uas_model",
        "flight_controller",
        "serial_number",
        "affected_subsystem_component",
        "reported_by",
    ]
    ordering_fields = ["created_at", "date_of_occurrence", "reported_date"]