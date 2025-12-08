# backend_app/drone_image/views.py

from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import DroneImage
from .serializers import DroneImageSerializer

class DroneImageListCreateView(generics.ListCreateAPIView):
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


# If you want GET + DELETE only:
class DroneImageRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer

