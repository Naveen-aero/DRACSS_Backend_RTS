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


from rest_framework import serializers
from .models import (
    DroneImage,
    DroneExtraImage,
    DroneAttachment,
    DroneTutorialVideo,
    DroneTroubleshootingVideo,
)
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
        # Allow JSON string OR dict
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = {}
        return super().to_internal_value(data)


# -------- CHILD SERIALIZERS ----------
class DroneExtraImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneExtraImage
        fields = ["id", "image"]


class DroneAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneAttachment
        fields = ["id", "file"]


class DroneTutorialVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneTutorialVideo
        fields = ["id", "file"]


class DroneTroubleshootingVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneTroubleshootingVideo
        fields = ["id", "file"]


# -------- MAIN DRONE SERIALIZER ----------
class DroneImageSerializer(serializers.ModelSerializer):
    specification = SpecificationSerializer(required=False)

    images = DroneExtraImageSerializer(many=True, read_only=True)
    attachments = DroneAttachmentSerializer(many=True, read_only=True)
    tutorial_videos = DroneTutorialVideoSerializer(many=True, read_only=True)
    troubleshooting_videos = DroneTroubleshootingVideoSerializer(many=True, read_only=True)

    class Meta:
        model = DroneImage
        fields = [
            "id",
            "name",
            "image",
            "specification",
            "images",
            "attachments",
            "tutorial_videos",
            "troubleshooting_videos",
            "created_at",
        ]

    def create(self, validated_data):
        spec_data = validated_data.pop("specification", None)
        instance = DroneImage.objects.create(**validated_data)
        if spec_data is not None:
            instance.specification = spec_data
            instance.save()
        return instance

    def update(self, instance, validated_data):
        spec_data = validated_data.pop("specification", None)
        if spec_data is not None:
            instance.specification = spec_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
