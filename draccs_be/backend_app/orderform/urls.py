# backend_app/orderform/urls.py

from rest_framework.routers import DefaultRouter
from .views import (
    ChecklistItemViewSet,
    OrderViewSet,
    OrderItemViewSet,                 # ADDED
    OrderDeliveryInfoViewSet,
    OrderDeliveryAttachmentViewSet,   # NEW VIEWSET
)

router = DefaultRouter()

# Checklist templates
router.register(r"checklist-items", ChecklistItemViewSet, basename="checklist-items")

# Orders (with nested items + delivery_info)
router.register(r"orders", OrderViewSet, basename="orders")

# 👇 NEW: endpoint for each checklist line item (OrderItem)
router.register(r"order-items", OrderItemViewSet, basename="order-items")

# Delivery info (UIN + ready_for_delivery flag)
router.register(r"order-delivery-info", OrderDeliveryInfoViewSet, basename="order-delivery-info")

# NEW ENDPOINT FOR MULTIPLE ATTACHMENTS
router.register(
    r"order-delivery-attachments",
    OrderDeliveryAttachmentViewSet,
    basename="order-delivery-attachments",
)

urlpatterns = router.urls
