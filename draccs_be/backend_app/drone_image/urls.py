from django.urls import path
from .views import (
    DroneImageListCreateView,
    DroneImageRetrieveUpdateDestroyView,
    DroneExtraImageDestroyView,
)

urlpatterns = [
    # List + Create
    path("drone_images/", DroneImageListCreateView.as_view(), name="drone-images"),

    # Retrieve + Update + Delete (whole drone record)
    path(
        "drone_images/<int:pk>/",
        DroneImageRetrieveUpdateDestroyView.as_view(),
        name="drone-image-detail",
    ),

    # Delete a SINGLE extra image (by its id in images[])
    path(
        "drone_images/extra/<int:pk>/",
        DroneExtraImageDestroyView.as_view(),
        name="drone-extra-image-destroy",
    ),
]
