from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import DroneImage
from .serializers import DroneImageSerializer  #  plural

class DroneImageListCreateView(generics.ListCreateAPIView):
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class DroneImageRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
