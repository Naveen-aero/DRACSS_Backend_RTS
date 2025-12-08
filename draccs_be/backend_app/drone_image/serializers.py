# # backend_app/drone_image/serializers.py

# from rest_framework import serializers
# from .models import DroneImage

# # Nested specification structure
# class SpecificationSerializer(serializers.Serializer):
#     weight = serializers.CharField(required=False, allow_blank=True)
#     dimensions = serializers.CharField(required=False, allow_blank=True)
#     speed = serializers.CharField(required=False, allow_blank=True)
#     takeoff_altitude = serializers.CharField(required=False, allow_blank=True)
#     flight_time = serializers.CharField(required=False, allow_blank=True)
#     flight_distance = serializers.CharField(required=False, allow_blank=True)


# class DroneImageSerializer(serializers.ModelSerializer):
#     specification = SpecificationSerializer(required=False)

#     class Meta:
#         model = DroneImage
#         fields = [
#             "id",
#             "name",
#             "image",
#             "specification",
#             "tutorial_video",        
#             "troubleshooting_video", 
#             "created_at",
#         ]

#     def create(self, validated_data):
#         spec_data = validated_data.pop("specification", {})
#         validated_data["specification"] = spec_data
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         spec_data = validated_data.pop("specification", None)
#         if spec_data is not None:
#             instance.specification = spec_data
#         return super().update(instance, validated_data)

import json
from rest_framework import serializers
from .models import DroneImage
 
class SpecificationSerializer(serializers.Serializer):
    weight = serializers.CharField(required=False, allow_blank=True)
    dimensions = serializers.CharField(required=False, allow_blank=True)
    speed = serializers.CharField(required=False, allow_blank=True)
    takeoff_altitude = serializers.CharField(required=False, allow_blank=True)
    flight_time = serializers.CharField(required=False, allow_blank=True)
    flight_distance = serializers.CharField(required=False, allow_blank=True)
 
    def to_internal_value(self, data):
        # Convert string to dict if coming from FormData
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = {}
        return super().to_internal_value(data)
 
class DroneImageSerializer(serializers.ModelSerializer):
    # JSONField will handle both dict and JSON string from FormData
    specification = serializers.JSONField(required=False)
 
    class Meta:
        model = DroneImage
        fields = [
            "id",
            "name",
            "image",
            "specification",
            "tutorial_video",
            "troubleshooting_video",
            "created_at",
        ]
 
    def create(self, validated_data):
        spec_data = validated_data.pop("specification", None)
        if spec_data is not None:
            if isinstance(spec_data, str):
                try:
                    spec_data = json.loads(spec_data)
                except json.JSONDecodeError:
                    spec_data = {}
            validated_data["specification"] = spec_data
        return super().create(validated_data)
 
    def update(self, instance, validated_data):
        spec_data = validated_data.pop("specification", None)
        if spec_data is not None:
            if isinstance(spec_data, str):
                try:
                    spec_data = json.loads(spec_data)
                except json.JSONDecodeError:
                    spec_data = {}
            # Merge with existing specification instead of overwriting
            instance.specification = {*(instance.specification or {}), *spec_data}
 
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
 
        instance.save()
        return instance