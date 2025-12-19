# from rest_framework.routers import DefaultRouter
# from .views import SupportThreadViewSet

# router = DefaultRouter()
# router.register(r"threads", SupportThreadViewSet, basename="support-thread")

# urlpatterns = router.urls


from rest_framework.routers import DefaultRouter
from .views import SupportThreadViewSet

router = DefaultRouter()
router.register(r"threads", SupportThreadViewSet, basename="support-thread")

urlpatterns = router.urls
