from django.urls import path
from .views import (
    DroneImageListCreateView,
    DroneImageRetrieveUpdateDestroyView,
    DroneExtraImageDestroyView,
)

urlpatterns = [
    # List + Create
    path(
        "drone_images/",
        DroneImageListCreateView.as_view(),
        name="drone-images",
    ),

    # Retrieve + Update + Delete whole drone record
    path(
        "drone_images/<int:pk>/",
        DroneImageRetrieveUpdateDestroyView.as_view(),
        name="drone-image-detail",
    ),

    # Delete a SINGLE extra image for a given drone
    # Example: DELETE /api/drone_images/1/images/2/
    path(
        "drone_images/<int:drone_pk>/images/<int:pk>/",
        DroneExtraImageDestroyView.as_view(),
        name="drone-extra-image-destroy",
    ),
]
