from rest_framework import viewsets, permissions, filters
from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """
    /api/clients/
    /api/clients/<client_id>/

    Full CRUD for Client table.
    """

    queryset = Client.objects.all().order_by("-created_at")
    serializer_class = ClientSerializer

    # adjust permission as you like
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = [
        "client_id",
        "name",
        "phone",
        "email",
        "location",
        "id_proof",
        "bank_name",
        "account_number",
        "ifsc_code",
        "branch_name",
    ]

    ordering_fields = [
        "created_at",
        "name",
        "location",
    ]
    ordering = ["-created_at"]
