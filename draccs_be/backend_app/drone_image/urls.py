from django.urls import path
from .views import (
    DroneImageListCreateView,
    DroneImageRetrieveUpdateDestroyView,
    DroneExtraImageListCreateView,
    DroneExtraImageRetrieveDestroyView,
    DroneAttachmentListCreateView,
    DroneAttachmentRetrieveDestroyView,
    DroneTutorialVideoListCreateView,
    DroneTutorialVideoRetrieveDestroyView,
    DroneTroubleshootingVideoListCreateView,
    DroneTroubleshootingVideoRetrieveDestroyView,
)

urlpatterns = [
    # Drone master
    path("drone_images/", DroneImageListCreateView.as_view(), name="droneimage-list-create"),
    path("drone_images/<int:pk>/", DroneImageRetrieveUpdateDestroyView.as_view(), name="droneimage-detail"),

    # Extra images
    path("drone_extra_images/", DroneExtraImageListCreateView.as_view(), name="droneextraimage-list-create"),
    path("drone_extra_images/<int:pk>/", DroneExtraImageRetrieveDestroyView.as_view(), name="droneextraimage-detail"),

    # Attachments
    path("drone_attachments/", DroneAttachmentListCreateView.as_view(), name="droneattachment-list-create"),
    path("drone_attachments/<int:pk>/", DroneAttachmentRetrieveDestroyView.as_view(), name="droneattachment-detail"),

    # Tutorial videos
    path("drone_tutorial_videos/", DroneTutorialVideoListCreateView.as_view(), name="dronetutorialvideo-list-create"),
    path("drone_tutorial_videos/<int:pk>/", DroneTutorialVideoRetrieveDestroyView.as_view(), name="dronetutorialvideo-detail"),

    # Troubleshooting videos
    path(
        "drone_troubleshooting_videos/",
        DroneTroubleshootingVideoListCreateView.as_view(),
        name="dronetroubleshootingvideo-list-create",
    ),
    path(
        "drone_troubleshooting_videos/<int:pk>/",
        DroneTroubleshootingVideoRetrieveDestroyView.as_view(),
        name="dronetroubleshootingvideo-detail",
    ),
]
