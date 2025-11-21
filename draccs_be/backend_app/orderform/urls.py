from rest_framework.routers import DefaultRouter
from .views import (
    ChecklistItemViewSet,
    OrderViewSet,
    OrderDeliveryInfoViewSet,
    OrderDeliveryAttachmentViewSet,   # NEW VIEWSET
)

router = DefaultRouter()
router.register(r"checklist-items", ChecklistItemViewSet, basename="checklist-items")
router.register(r"orders", OrderViewSet, basename="orders")
router.register(r"order-delivery-info", OrderDeliveryInfoViewSet, basename="order-delivery-info")

# NEW ENDPOINT FOR MULTIPLE ATTACHMENTS
router.register(
    r"order-delivery-attachments",
    OrderDeliveryAttachmentViewSet,
    basename="order-delivery-attachments"
)

urlpatterns = router.urls
