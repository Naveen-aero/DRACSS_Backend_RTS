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


# ---------- DRONE MASTER ----------

class DroneImageListCreateView(generics.ListCreateAPIView):
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class DroneImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


# ---------- EXTRA IMAGES ----------

class DroneExtraImageListCreateView(generics.ListCreateAPIView):
    """
    POST /api/drone_extra_images/
      - form-data:
         - drone: <drone_id>
         - image: <file>
    GET /api/drone_extra_images/?drone=<id>  (filter by drone)
    """
    serializer_class = DroneExtraImageSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = DroneExtraImage.objects.all()
        drone_id = self.request.query_params.get("drone")
        if drone_id:
            qs = qs.filter(drone_id=drone_id)
        return qs


class DroneExtraImageRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = DroneExtraImage.objects.all()
    serializer_class = DroneExtraImageSerializer


# ---------- ATTACHMENTS ----------

class DroneAttachmentListCreateView(generics.ListCreateAPIView):
    """
    POST /api/drone_attachments/
      - form-data:
         - drone: <drone_id>
         - file: <file>
    GET /api/drone_attachments/?drone=<id>
    """
    serializer_class = DroneAttachmentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = DroneAttachment.objects.all()
        drone_id = self.request.query_params.get("drone")
        if drone_id:
            qs = qs.filter(drone_id=drone_id)
        return qs


class DroneAttachmentRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = DroneAttachment.objects.all()
    serializer_class = DroneAttachmentSerializer


# ---------- TUTORIAL VIDEOS ----------

class DroneTutorialVideoListCreateView(generics.ListCreateAPIView):
    """
    POST /api/drone_tutorial_videos/
      - form-data:
         - drone: <drone_id>
         - video: <file>
    GET /api/drone_tutorial_videos/?drone=<id>
    """
    serializer_class = DroneTutorialVideoSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = DroneTutorialVideo.objects.all()
        drone_id = self.request.query_params.get("drone")
        if drone_id:
            qs = qs.filter(drone_id=drone_id)
        return qs


class DroneTutorialVideoRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = DroneTutorialVideo.objects.all()
    serializer_class = DroneTutorialVideoSerializer


# ---------- TROUBLESHOOTING VIDEOS ----------

class DroneTroubleshootingVideoListCreateView(generics.ListCreateAPIView):
    """
    POST /api/drone_troubleshooting_videos/
      - form-data:
         - drone: <drone_id>
         - video: <file>
    GET /api/drone_troubleshooting_videos/?drone=<id>
    """
    serializer_class = DroneTroubleshootingVideoSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = DroneTroubleshootingVideo.objects.all()
        drone_id = self.request.query_params.get("drone")
        if drone_id:
            qs = qs.filter(drone_id=drone_id)
        return qs


class DroneTroubleshootingVideoRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = DroneTroubleshootingVideo.objects.all()
    serializer_class = DroneTroubleshootingVideoSerializer
