from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser  #  ADD JSONParser
from .models import DroneRegistration
from .serializers import DroneRegistrationSerializer


class DroneRegistrationViewSet(viewsets.ModelViewSet):
    queryset = DroneRegistration.objects.all()
    serializer_class = DroneRegistrationSerializer

    # If you later want auth, switch this back to IsAuthenticated, etc.
    permission_classes = [permissions.AllowAny]

    #  Allow JSON + form + multipart uploads
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "model_name",
        "uin_number",
        "drone_serial_number",
        "drone_id", 
        "manufacturer",
    ]
    ordering_fields = ["created_at", "model_name", "manufacturer", "registered"]
    ordering = ["-created_at"]
