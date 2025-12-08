from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import DroneImage
from .serializers import DroneImageSerializer


class DroneImageListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/drone_images/   -> list all drone images
    POST /api/drone_images/   -> create new drone image (with image, spec, videos)
    """
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class DroneImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/drone_images/<id>/ -> retrieve one
    PUT    /api/drone_images/<id>/ -> full update
    PATCH  /api/drone_images/<id>/ -> partial update
    DELETE /api/drone_images/<id>/ -> delete record + files
    """
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
