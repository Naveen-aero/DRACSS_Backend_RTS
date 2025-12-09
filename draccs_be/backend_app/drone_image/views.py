from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import DroneImage, DroneExtraImage
from .serializers import DroneImageSerializer, DroneExtraImageSerializer


class DroneImageListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/drone_images/      -> list all drone images
    POST /api/drone_images/      -> create new drone image (with image, spec, videos, extra images)
    """
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class DroneImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/drone_images/<id>/ -> retrieve one
    PUT    /api/drone_images/<id>/ -> full update
    PATCH  /api/drone_images/<id>/ -> partial update
    DELETE /api/drone_images/<id>/ -> delete record + all files
    """
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class DroneExtraImageDestroyView(generics.DestroyAPIView):
    """
    DELETE /api/drone_images/extra/<id>/ -> delete a single extra image
    """
    queryset = DroneExtraImage.objects.all()
    serializer_class = DroneExtraImageSerializer
    # default parsers are fine for DELETE; no need for MultiPartParser here
