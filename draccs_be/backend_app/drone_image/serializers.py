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


class DroneExtraImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneExtraImage
        fields = ["id", "image", "drone"]


class DroneAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneAttachment
        fields = ["id", "file", "drone"]


class DroneTutorialVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneTutorialVideo
        fields = ["id", "video", "drone"]


class DroneTroubleshootingVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneTroubleshootingVideo
        fields = ["id", "video", "drone"]


class DroneImageSerializer(serializers.ModelSerializer):
    # Nested, read-only lists
    images = DroneExtraImageSerializer(many=True, read_only=True)
    tutorial_videos = DroneTutorialVideoSerializer(many=True, read_only=True)
    troubleshooting_videos = DroneTroubleshootingVideoSerializer(many=True, read_only=True)
    attachments = DroneAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = DroneImage
        fields = [
            "id",
            "name",
            "image",
            "specification",
            "tutorial_videos",
            "troubleshooting_videos",
            "images",
            "attachments",
            "created_at",
        ]
