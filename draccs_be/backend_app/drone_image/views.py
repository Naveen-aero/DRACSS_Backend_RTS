# from rest_framework import generics
# from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# from .models import DroneImage, DroneExtraImage
# from .serializers import DroneImageSerializer, DroneExtraImageSerializer


# class DroneImageListCreateView(generics.ListCreateAPIView):
#     queryset = DroneImage.objects.all()
#     serializer_class = DroneImageSerializer
#     parser_classes = [MultiPartParser, FormParser, JSONParser]


# class DroneImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = DroneImage.objects.all()
#     serializer_class = DroneImageSerializer
#     parser_classes = [MultiPartParser, FormParser, JSONParser]


# class DroneExtraImageRetrieveDestroyView(generics.RetrieveDestroyAPIView):
#     """
#     Handle a single extra image for a specific DroneImage:
#     GET    /api/drone_images/<drone_id>/images/<pk>/
#     DELETE /api/drone_images/<drone_id>/images/<pk>/
#     """
#     serializer_class = DroneExtraImageSerializer

#     def get_queryset(self):
#         # Only allow images that belong to the given drone_id
#         drone_id = self.kwargs["drone_id"]
#         return DroneExtraImage.objects.filter(drone_id=drone_id)


from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import (
    DroneImage,
    DroneExtraImage,
    DroneTutorialVideo,
    DroneTroubleshootingVideo,
)
from .serializers import (
    DroneImageSerializer,
    DroneExtraImageSerializer,
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


class DroneExtraImageRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    """
    Handle a single extra image for a specific DroneImage:
    GET    /api/drone_images/<drone_id>/images/<pk>/
    DELETE /api/drone_images/<drone_id>/images/<pk>/
    """
    serializer_class = DroneExtraImageSerializer

    def get_queryset(self):
        drone_id = self.kwargs["drone_id"]
        return DroneExtraImage.objects.filter(drone_id=drone_id)


class DroneTutorialVideoRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    """
    Single tutorial video for a specific DroneImage:
    GET    /api/drone_images/<drone_id>/tutorial_videos/<pk>/
    DELETE /api/drone_images/<drone_id>/tutorial_videos/<pk>/
    """
    serializer_class = DroneTutorialVideoSerializer

    def get_queryset(self):
        drone_id = self.kwargs["drone_id"]
        return DroneTutorialVideo.objects.filter(drone_id=drone_id)


class DroneTroubleshootingVideoRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    """
    Single troubleshooting video for a specific DroneImage:
    GET    /api/drone_images/<drone_id>/troubleshooting_videos/<pk>/
    DELETE /api/drone_images/<drone_id>/troubleshooting_videos/<pk>/
    """
    serializer_class = DroneTroubleshootingVideoSerializer

    def get_queryset(self):
        drone_id = self.kwargs["drone_id"]
        return DroneTroubleshootingVideo.objects.filter(drone_id=drone_id)
