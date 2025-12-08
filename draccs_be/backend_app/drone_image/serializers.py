# drone_registration/serializer.py
from rest_framework import serializers
from .models import DroneImage

class DroneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneImage
        fields = ['id', 'name', 'image', 'created_at']
