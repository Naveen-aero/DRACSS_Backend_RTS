# backend_app/orderform/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import (
    ChecklistItem,
    Order,
    OrderDeliveryInfo,
    OrderDeliveryAttachment,   # NEW
)
from .serializers import (
    ChecklistItemSerializer,
    OrderSerializer,
    OrderDeliveryInfoSerializer,
    OrderDeliveryAttachmentSerializer,   # NEW
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
      - Set UIN registration number
      - Toggle ready_for_delivery flag

    NOTE:
      Attachments (manufacturer/testing) are managed via
      /api/order-delivery-attachments/, not here.

    POST behaviour:
      - If delivery info for 'order' exists -> update it
      - If not -> create a new one
    """
    queryset = OrderDeliveryInfo.objects.select_related("order").all()
    serializer_class = OrderDeliveryInfoSerializer

    def create(self, request, *args, **kwargs):
        """
        Upsert-style:
          - request.data MUST contain 'order' (Order ID)
          - If an OrderDeliveryInfo already exists for that order -> update it
          - Else -> create it, then update fields
        """
        order_id = request.data.get("order")

        if not order_id:
            return Response(
                {"detail": "Field 'order' (Order ID) is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create the row for this order
        delivery_info, created = OrderDeliveryInfo.objects.get_or_create(
            order_id=order_id
        )

        # Now apply the incoming data (uin_registration_number, ready_for_delivery, etc.)
        serializer = self.get_serializer(
            delivery_info, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class OrderDeliveryAttachmentViewSet(viewsets.ModelViewSet):
    """
    /api/order-delivery-attachments/
    /api/order-delivery-attachments/<id>/

    Use this to upload and manage attachments:

      POST (multipart/form-data):
        - order:          <Order.id>  (e.g., 1)
        - attachment_type: "MANUFACTURER" or "TESTING"
        - file:           <single file>

      You can call POST multiple times to add many files.
    """
    queryset = (
        OrderDeliveryAttachment.objects
        .select_related("delivery_info", "delivery_info__order")
        .all()
    )
    serializer_class = OrderDeliveryAttachmentSerializer
