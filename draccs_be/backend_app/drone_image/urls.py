from django.urls import path
from .views import (
    DroneImageListCreateView,
    DroneImageRetrieveDestroyView,
)

urlpatterns = [
    # List + Create
    path("drone_images/", DroneImageListCreateView.as_view(), name="drone-images"),

    # Retrieve + Delete (and could be used for future PUT/PATCH)
    path(
        "drone_images/<int:pk>/",
        DroneImageRetrieveDestroyView.as_view(),
        name="drone-image-detail",
    ),
]
