from rest_framework.routers import DefaultRouter
from .views import (
    ChecklistItemViewSet,
    OrderViewSet,
    # OrderItemViewSet,
    OrderDeliveryInfoViewSet,
)

router = DefaultRouter()
router.register(r"checklist-items", ChecklistItemViewSet, basename="checklist-items")
router.register(r"orders", OrderViewSet, basename="orders")
# router.register(r"order-items", OrderItemViewSet, basename="order-items")
router.register(r"order-delivery-info", OrderDeliveryInfoViewSet, basename="order-delivery-info")

urlpatterns = router.urls
