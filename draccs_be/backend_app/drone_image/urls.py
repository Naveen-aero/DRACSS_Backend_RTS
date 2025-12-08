from django.urls import path
from .views import DroneImageListCreateView

urlpatterns = [
    path("drone_images/", DroneImageListCreateView.as_view(), name="drone-images"),
]
