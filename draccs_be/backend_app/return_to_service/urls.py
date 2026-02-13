from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReturnToBaseServiceRequestViewSet

router = DefaultRouter()
router.register(r"rtb-service-requests", ReturnToBaseServiceRequestViewSet, basename="rtb-service-requests")

urlpatterns = [
    path("", include(router.urls)),
]