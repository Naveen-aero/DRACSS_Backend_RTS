# backend_app/drone_image/urls.py

from django.urls import path
from .views import (
    DroneImageListCreateView,
    DroneImageRetrieveDestroyView,
)

urlpatterns = [
    # List + Create → /api/drone_images/
    path("drone_images/", DroneImageListCreateView.as_view(), name="drone-images"),

    # Retrieve + Delete (and optionally Update) → /api/drone_images/<id>/
    path(
        "drone_images/<int:pk>/",
        DroneImageRetrieveDestroyView.as_view(),
        name="drone-image-detail",
    ),
]
