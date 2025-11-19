from rest_framework.routers import DefaultRouter
from .views import ChecklistItemViewSet, OrderViewSet

router = DefaultRouter()
router.register(r"checklist-items", ChecklistItemViewSet, basename="checklist-item")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = router.urls
