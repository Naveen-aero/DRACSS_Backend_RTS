# from rest_framework.routers import DefaultRouter
# from .views import SupportThreadViewSet

# router = DefaultRouter()
# router.register(r"threads", SupportThreadViewSet, basename="support-thread")

# urlpatterns = router.urls

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupportThreadViewSet, SupportMessageViewSet

router = DefaultRouter()
router.register(r"threads", SupportThreadViewSet, basename="threads")
router.register(r"messages", SupportMessageViewSet, basename="messages")

urlpatterns = [
    path("", include(router.urls)),
]
