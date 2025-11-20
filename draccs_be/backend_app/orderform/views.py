# backend_app/orderform/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response

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

    POST behaviour:
      - If delivery info for 'order' exists -> update it
      - If not -> create a new one
    """
    queryset = OrderDeliveryInfo.objects.select_related("order").all()
    serializer_class = OrderDeliveryInfoSerializer

    def create(self, request, *args, **kwargs):
        """
        Override POST so that:
        - It updates existing OrderDeliveryInfo for the given 'order'
        - Or creates a new one if none exists.
        """
        order_id = request.data.get("order")

        if not order_id:
            return Response(
                {"detail": "Field 'order' (Order ID) is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Does a row already exist for this order?
            instance = OrderDeliveryInfo.objects.get(order_id=order_id)
        except OrderDeliveryInfo.DoesNotExist:
            # No existing row -> normal create
            return super().create(request, *args, **kwargs)

        # Existing row -> update it (partial update, so you can send only changed fields)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
