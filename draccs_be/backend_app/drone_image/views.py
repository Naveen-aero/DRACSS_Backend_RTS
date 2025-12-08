# drone_registration/views.py
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from .models import DroneImage
from .serializers import DroneImageSerializer

class DroneImageListCreateView(generics.ListCreateAPIView):
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
    parser_classes = [MultiPartParser, FormParser]  # needed for file upload
