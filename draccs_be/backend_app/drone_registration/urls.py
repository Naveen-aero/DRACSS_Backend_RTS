from rest_framework.routers import DefaultRouter
from .views import DroneRegistrationViewSet

router = DefaultRouter()
router.register(r'drone_registration', DroneRegistrationViewSet, basename='drone-registration')

urlpatterns = router.urls
