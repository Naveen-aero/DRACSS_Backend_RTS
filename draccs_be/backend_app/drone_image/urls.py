# from django.urls import path
# from .views import (
#     DroneImageListCreateView,
#     DroneImageRetrieveUpdateDestroyView,
#     DroneExtraImageRetrieveDestroyView,
# )

# urlpatterns = [
#     # List all drones / create new
#     path("drone_images/", DroneImageListCreateView.as_view(), name="droneimage-list-create"),

#     # Single drone: GET, PUT/PATCH, DELETE
#     path(
#         "drone_images/<int:pk>/",
#         DroneImageRetrieveUpdateDestroyView.as_view(),
#         name="droneimage-detail",
#     ),

#     # Single extra image for a given drone:
#     # e.g. /api/drone_images/1/images/3/
#     path(
#         "drone_images/<int:drone_id>/images/<int:pk>/",
#         DroneExtraImageRetrieveDestroyView.as_view(),
#         name="droneextraimage-detail",
#     ),
# ]
from django.urls import path
from .views import (
    DroneImageListCreateView,
    DroneImageRetrieveUpdateDestroyView,
    DroneExtraImageRetrieveDestroyView,
    DroneTutorialVideoRetrieveDestroyView,
    DroneTroubleshootingVideoRetrieveDestroyView,
    TutorialVideoUploadView,          
    TroubleshootingVideoUploadView,   
)

urlpatterns = [
    # List all drones / create new
    path(
        "drone_images/",
        DroneImageListCreateView.as_view(),
        name="droneimage-list-create",
    ),

    # Single drone: GET, PUT/PATCH, DELETE
    path(
        "drone_images/<int:pk>/",
        DroneImageRetrieveUpdateDestroyView.as_view(),
        name="droneimage-detail",
    ),

    #  NEW: upload tutorial videos for a drone
    path(
        "drone_images/<int:pk>/tutorial/",
        TutorialVideoUploadView.as_view(),
        name="droneimage-tutorial-upload",
    ),

    #  NEW: upload troubleshooting videos for a drone
    path(
        "drone_images/<int:pk>/troubleshooting/",
        TroubleshootingVideoUploadView.as_view(),
        name="droneimage-troubleshooting-upload",
    ),

    # Single extra image (GET/DELETE)
    path(
        "drone_images/<int:drone_id>/images/<int:pk>/",
        DroneExtraImageRetrieveDestroyView.as_view(),
        name="droneextraimage-detail",
    ),

    # Single tutorial video (GET/DELETE)
    path(
        "drone_images/<int:drone_id>/tutorial_videos/<int:pk>/",
        DroneTutorialVideoRetrieveDestroyView.as_view(),
        name="dronetutorialvideo-detail",
    ),

    # Single troubleshooting video (GET/DELETE)
    path(
        "drone_images/<int:drone_id>/troubleshooting_videos/<int:pk>/",
        DroneTroubleshootingVideoRetrieveDestroyView.as_view(),
        name="dronetroubleshootingvideo-detail",
    ),
]

