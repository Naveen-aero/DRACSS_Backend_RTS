# backend_app/orderform/views.py

from rest_framework import viewsets
from .models import (
    ChecklistItem,
    Order,
    OrderDeliveryInfo,
)
from .serializers import (
    ChecklistItemSerializer,
    OrderSerializer,
    OrderDeliveryInfoSerializer,
)


class ChecklistItemViewSet(viewsets.ModelViewSet):
    """
    /api/checklist-items/
    /api/checklist-items/<id>/
    """
    queryset = ChecklistItem.objects.all().order_by("sort_order")
    serializer_class = ChecklistItemSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    /api/orders/
    /api/orders/<id>/
    """
    queryset = (
        Order.objects
        .all()
        .select_related("delivery_info")  # 1:1 OrderDeliveryInfo
        .prefetch_related("items")        # related OrderItem rows (nested in serializer)
        .order_by("-id")
    )
    serializer_class = OrderSerializer


class OrderDeliveryInfoViewSet(viewsets.ModelViewSet):
    """
    /api/order-delivery-info/
    /api/order-delivery-info/<order_id>/

    Use this to:
      - Upload manufacturer/testing attachments
      - Set UIN registration number
      - Toggle ready_for_delivery flag
    """
    queryset = OrderDeliveryInfo.objects.select_related("order").all()
    serializer_class = OrderDeliveryInfoSerializer
