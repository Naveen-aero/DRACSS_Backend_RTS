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

from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

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


# ---------- NEW: UPLOAD MULTIPLE TUTORIAL VIDEOS FOR ONE DRONE ----------

class TutorialVideoUploadView(generics.CreateAPIView):
    """
    POST /api/drone_images/<pk>/tutorial/
    - Field name for files: "videos" (can be multiple)
    """
    serializer_class = DroneTutorialVideoSerializer
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk, *args, **kwargs):
        # Ensure parent drone exists
        drone = get_object_or_404(DroneImage, pk=pk)

        # Expect multiple files under key "videos"
        files = request.FILES.getlist("videos")
        if not files:
            return Response(
                {"detail": "No files found under 'videos'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_objects = []
        for f in files:
            obj = DroneTutorialVideo.objects.create(drone=drone, video=f)
            created_objects.append(obj)

        # Serialize and return all created videos
        serializer = self.get_serializer(created_objects, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ---------- NEW: UPLOAD MULTIPLE TROUBLESHOOTING VIDEOS FOR ONE DRONE ----------

class TroubleshootingVideoUploadView(generics.CreateAPIView):
    """
    POST /api/drone_images/<pk>/troubleshooting/
    - Field name for files: "videos" (can be multiple)
    """
    serializer_class = DroneTroubleshootingVideoSerializer
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk, *args, **kwargs):
        # Ensure parent drone exists
        drone = get_object_or_404(DroneImage, pk=pk)

        # Expect multiple files under key "videos"
        files = request.FILES.getlist("videos")
        if not files:
            return Response(
                {"detail": "No files found under 'videos'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_objects = []
        for f in files:
            obj = DroneTroubleshootingVideo.objects.create(drone=drone, video=f)
            created_objects.append(obj)

        # Serialize and return all created videos
        serializer = self.get_serializer(created_objects, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
