# from django.urls import path
# from .views import (
#     DroneImageListCreateView,
#     DroneImageRetrieveUpdateDestroyView,
#     DroneExtraImageDestroyView,
# )

# urlpatterns = [
#     # List + Create
#     path(
#         "drone_images/",
#         DroneImageListCreateView.as_view(),
#         name="drone-images",
#     ),

#     # Retrieve + Update + Delete whole drone record
#     path(
#         "drone_images/<int:pk>/",
#         DroneImageRetrieveUpdateDestroyView.as_view(),
#         name="drone-image-detail",
#     ),

#     # Delete a SINGLE extra image for a given drone
#     # Example: DELETE /api/drone_images/1/images/2/
#     path(
#         "drone_images/<int:drone_pk>/images/<int:pk>/",
#         DroneExtraImageDestroyView.as_view(),
#         name="drone-extra-image-destroy",
#     ),
# ]

from django.urls import path
from .views import (
    DroneImageListCreateView,
    DroneImageRetrieveUpdateDestroyView,
    DroneExtraImageDestroyView,
    DroneAttachmentDestroyView,
    DroneTutorialVideoDestroyView,
    DroneTroubleshootingVideoDestroyView,
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

    # Delete a SINGLE extra image
    # DELETE /api/drone_images/<drone_pk>/images/<pk>/
    path(
        "drone_images/<int:drone_pk>/images/<int:pk>/",
        DroneExtraImageDestroyView.as_view(),
        name="drone-extra-image-destroy",
    ),

    # Delete a SINGLE attachment
    # DELETE /api/drone_images/<drone_pk>/attachments/<pk>/
    path(
        "drone_images/<int:drone_pk>/attachments/<int:pk>/",
        DroneAttachmentDestroyView.as_view(),
        name="drone-attachment-destroy",
    ),

    # Delete a SINGLE tutorial video
    # DELETE /api/drone_images/<int:drone_pk>/tutorial_videos/<int:pk>/
    path(
        "drone_images/<int:drone_pk>/tutorial_videos/<int:pk>/",
        DroneTutorialVideoDestroyView.as_view(),
        name="drone-tutorial-video-destroy",
    ),

    # Delete a SINGLE troubleshooting video
    # DELETE /api/drone_images/<int:drone_pk>/troubleshooting_videos/<int:pk>/
    path(
        "drone_images/<int:drone_pk>/troubleshooting_videos/<int:pk>/",
        DroneTroubleshootingVideoDestroyView.as_view(),
        name="drone-troubleshooting-video-destroy",
    ),
]
