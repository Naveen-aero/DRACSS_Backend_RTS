# from rest_framework import generics
# from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# from .models import DroneImage, DroneExtraImage
# from .serializers import DroneImageSerializer, DroneExtraImageSerializer


# class DroneImageListCreateView(generics.ListCreateAPIView):
#     """
#     GET  /api/drone_images/      -> list all drone images
#     POST /api/drone_images/      -> create new drone image
#     """
#     queryset = DroneImage.objects.all()
#     serializer_class = DroneImageSerializer
#     parser_classes = [MultiPartParser, FormParser, JSONParser]


# class DroneImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
#     """
#     GET    /api/drone_images/<id>/ -> retrieve one
#     PUT    /api/drone_images/<id>/ -> full update
#     PATCH  /api/drone_images/<id>/ -> partial update
#     DELETE /api/drone_images/<id>/ -> delete record + all files
#     """
#     queryset = DroneImage.objects.all()
#     serializer_class = DroneImageSerializer
#     parser_classes = [MultiPartParser, FormParser, JSONParser]


# class DroneExtraImageDestroyView(generics.DestroyAPIView):
#     """
#     DELETE /api/drone_images/<drone_pk>/images/<pk>/
#     -> delete a single extra image that belongs to that drone
#     """
#     serializer_class = DroneExtraImageSerializer

#     def get_queryset(self):
#         # Only allow deleting images attached to this specific drone
#         drone_id = self.kwargs["drone_pk"]
#         return DroneExtraImage.objects.filter(drone_id=drone_id)

from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import (
    DroneImage,
    DroneExtraImage,
    DroneAttachment,
    DroneTutorialVideo,
    DroneTroubleshootingVideo,
)
from .serializers import (
    DroneImageSerializer,
    DroneExtraImageSerializer,
    DroneAttachmentSerializer,
    DroneTutorialVideoSerializer,
    DroneTroubleshootingVideoSerializer,
)


class DroneImageListCreateView(generics.ListCreateAPIView):
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class DroneImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class DroneExtraImageDestroyView(generics.DestroyAPIView):
    serializer_class = DroneExtraImageSerializer
    lookup_field = "pk"

    def get_queryset(self):
        drone_id = self.kwargs["drone_pk"]
        return DroneExtraImage.objects.filter(drone_id=drone_id)


class DroneAttachmentDestroyView(generics.DestroyAPIView):
    serializer_class = DroneAttachmentSerializer
    lookup_field = "pk"

    def get_queryset(self):
        drone_id = self.kwargs["drone_pk"]
        return DroneAttachment.objects.filter(drone_id=drone_id)


class DroneTutorialVideoDestroyView(generics.DestroyAPIView):
    """
    DELETE /api/drone_images/<drone_pk>/tutorial_videos/<pk>/
    """
    serializer_class = DroneTutorialVideoSerializer
    lookup_field = "pk"

    def get_queryset(self):
        drone_id = self.kwargs["drone_pk"]
        return DroneTutorialVideo.objects.filter(drone_id=drone_id)


class DroneTroubleshootingVideoDestroyView(generics.DestroyAPIView):
    """
    DELETE /api/drone_images/<drone_pk>/troubleshooting_videos/<pk>/
    """
    serializer_class = DroneTroubleshootingVideoSerializer
    lookup_field = "pk"

    def get_queryset(self):
        drone_id = self.kwargs["drone_pk"]
        return DroneTroubleshootingVideo.objects.filter(drone_id=drone_id)
