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
from .models import DroneImage, DroneExtraImage
import json

# -------- SPECIFICATION SERIALIZER ----------
class SpecificationSerializer(serializers.Serializer):
    weight = serializers.CharField(required=False, allow_blank=True)
    dimensions = serializers.CharField(required=False, allow_blank=True)
    speed = serializers.CharField(required=False, allow_blank=True)
    takeoff_altitude = serializers.CharField(required=False, allow_blank=True)
    flight_time = serializers.CharField(required=False, allow_blank=True)
    flight_distance = serializers.CharField(required=False, allow_blank=True)

    def to_internal_value(self, data):
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except:
                data = {}
        return super().to_internal_value(data)


# -------- EXTRA IMAGES SERIALIZER ----------
class DroneExtraImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneExtraImage
        fields = ["id", "image"]


# -------- MAIN DRONE SERIALIZER ----------
class DroneImageSerializer(serializers.ModelSerializer):
    specification = SpecificationSerializer(required=False)
    images = DroneExtraImageSerializer(many=True, read_only=True)
    images_upload = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = DroneImage
        fields = [
            "id",
            "name",
            "image",
            "specification",
            "tutorial_video",
            "troubleshooting_video",
            "images",
            "images_upload",
            "created_at",
        ]

    def to_internal_value(self, data):
        # Accept images_upload[] from React FormData
        if "images_upload[]" in data:
            data.setlist("images_upload", data.getlist("images_upload[]"))
        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        spec_data = validated_data.pop("specification", None)
        extra_images = validated_data.pop("images_upload", [])

        # Ensure spec_data is a dict and overwrite
        if spec_data is not None:
            if isinstance(spec_data, str):
                try:
                    spec_data = json.loads(spec_data)
                except:
                    spec_data = {}
            instance.specification = spec_data

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Save extra images
        for img in extra_images:
            DroneExtraImage.objects.create(drone=instance, image=img)

        return instance
