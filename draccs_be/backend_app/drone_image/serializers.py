# backend_app/drone_image/serializers.py

from rest_framework import serializers
from .models import DroneImage

# Nested specification structure
class SpecificationSerializer(serializers.Serializer):
    weight = serializers.CharField(required=False, allow_blank=True)
    dimensions = serializers.CharField(required=False, allow_blank=True)
    speed = serializers.CharField(required=False, allow_blank=True)
    takeoff_altitude = serializers.CharField(required=False, allow_blank=True)
    flight_time = serializers.CharField(required=False, allow_blank=True)
    flight_distance = serializers.CharField(required=False, allow_blank=True)


class DroneImageSerializer(serializers.ModelSerializer):
    specification = SpecificationSerializer(required=False)

    class Meta:
        model = DroneImage
        fields = [
            "id",
            "name",
            "image",
            "specification",
            "created_at",   #  no extra spaces, exactly like this
        ]

    def create(self, validated_data):
        spec_data = validated_data.pop("specification", {})
        validated_data["specification"] = spec_data
        return super().create(validated_data)

    def update(self, instance, validated_data):
        spec_data = validated_data.pop("specification", None)
        if spec_data is not None:
            instance.specification = spec_data
        return super().update(instance, validated_data)
