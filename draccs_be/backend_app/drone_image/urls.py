from django.urls import path
from .views import (
    DroneImageListCreateView,
    DroneImageRetrieveUpdateDestroyView,
)

urlpatterns = [
    # List + Create
    path("drone_images/", DroneImageListCreateView.as_view(), name="drone-images"),

    # Retrieve + Update + Delete
    path(
        "drone_images/<int:pk>/",
        DroneImageRetrieveUpdateDestroyView.as_view(),
        name="drone-image-detail",
    ),
]
