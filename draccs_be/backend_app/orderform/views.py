from rest_framework import viewsets, permissions, filters
from .models import ChecklistItem, Order
from .serializers import ChecklistItemSerializer, OrderSerializer


class ChecklistItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    READ-ONLY master template.
    /api/checklist-items/ -> list
    /api/checklist-items/<id>/ -> detail
    No add/edit/delete allowed here.
    """
    queryset = ChecklistItem.objects.all().order_by("sort_order")
    serializer_class = ChecklistItemSerializer
    permission_classes = [permissions.AllowAny]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["description", "drone_model", "category"]
    ordering_fields = ["sort_order", "drone_model", "category"]
    ordering = ["sort_order"]


class OrderViewSet(viewsets.ModelViewSet):
    """
    Per-order editable checklist.

    - On create: if items not provided, pull from ChecklistItem and create OrderItem rows.
    - On update: items array is fully editable (add/remove/edit rows).
    """
    queryset = Order.objects.all().order_by("-created_at").prefetch_related("items")
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]  # tighten later if needed

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "order_number",
        "customer_name",
        "drone_model",
        "status",
    ]
    ordering_fields = ["created_at", "order_date", "order_number"]
    ordering = ["-created_at"]
