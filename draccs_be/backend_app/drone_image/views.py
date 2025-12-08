from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from .models import DroneImage
from .serializers import DroneImageSerializer   # or .serializers if that's your filename

# List + Create  →  /api/drone_images/
class DroneImageListCreateView(generics.ListCreateAPIView):
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
    parser_classes = [MultiPartParser, FormParser]


# Retrieve + Delete  →  /api/drone_images/<id>/
class DroneImageRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
