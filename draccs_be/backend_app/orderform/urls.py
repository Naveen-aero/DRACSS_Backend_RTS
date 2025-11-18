from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChecklistItemViewSet, OrderViewSet

router = DefaultRouter()
router.register(r"checklist-items", ChecklistItemViewSet, basename="checklistitem")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
]
