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


# -------- EXTRA IMAGES SERIALIZER ----------
class DroneExtraImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneExtraImage
        fields = ["id", "image"]


# -------- ATTACHMENTS SERIALIZER ----------
class DroneAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneAttachment
        fields = ["id", "file"]


# -------- TUTORIAL VIDEO SERIALIZER (MULTIPLE) ----------
class DroneTutorialVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneTutorialVideo
        fields = ["id", "file"]


# -------- TROUBLESHOOTING VIDEO SERIALIZER (MULTIPLE) ----------
class DroneTroubleshootingVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneTroubleshootingVideo
        fields = ["id", "file"]


# -------- MAIN DRONE SERIALIZER ----------
class DroneImageSerializer(serializers.ModelSerializer):
    specification = SpecificationSerializer(required=False)

    # Read-only nested lists
    images = DroneExtraImageSerializer(many=True, read_only=True)
    attachments = DroneAttachmentSerializer(many=True, read_only=True)
    tutorial_videos = DroneTutorialVideoSerializer(many=True, read_only=True)
    troubleshooting_videos = DroneTroubleshootingVideoSerializer(many=True, read_only=True)

    # Write-only for multiple uploads
    images_upload = serializers.ListField(
        child=serializers.ImageField(
            max_length=None,
            allow_empty_file=False,
            use_url=False,
        ),
        write_only=True,
        required=False,
    )

    attachments_upload = serializers.ListField(
        child=serializers.FileField(
            max_length=None,
            allow_empty_file=False,
            use_url=False,
        ),
        write_only=True,
        required=False,
    )

    tutorial_videos_upload = serializers.ListField(
        child=serializers.FileField(
            max_length=None,
            allow_empty_file=False,
            use_url=False,
        ),
        write_only=True,
        required=False,
    )

    troubleshooting_videos_upload = serializers.ListField(
        child=serializers.FileField(
            max_length=None,
            allow_empty_file=False,
            use_url=False,
        ),
        write_only=True,
        required=False,
    )

    class Meta:
        model = DroneImage
        fields = [
            "id",
            "name",
            "image",                    # main image (single)
            "specification",
            # NOTE: single tutorial_video / troubleshooting_video removed from here
            "images",                   # read-only extra images
            "attachments",              # read-only attachments
            "tutorial_videos",          # read-only list of tutorial videos
            "troubleshooting_videos",   # read-only list of troubleshooting videos
            "images_upload",            # write-only
            "attachments_upload",       # write-only
            "tutorial_videos_upload",   # write-only
            "troubleshooting_videos_upload",  # write-only
            "created_at",
        ]

    def to_internal_value(self, data):
        """
        Normalize React FormData keys:
        - images_upload[]
        - attachments_upload[]
        - tutorial_videos_upload[]
        - troubleshooting_videos_upload[]
        """
        if hasattr(data, "getlist"):
            data = data.copy()
            if "images_upload[]" in data:
                data.setlist("images_upload", data.getlist("images_upload[]"))
            if "attachments_upload[]" in data:
                data.setlist("attachments_upload", data.getlist("attachments_upload[]"))
            if "tutorial_videos_upload[]" in data:
                data.setlist("tutorial_videos_upload", data.getlist("tutorial_videos_upload[]"))
            if "troubleshooting_videos_upload[]" in data:
                data.setlist("troubleshooting_videos_upload", data.getlist("troubleshooting_videos_upload[]"))
        return super().to_internal_value(data)

    # -------- CREATE --------
    def create(self, validated_data):
        spec_data = validated_data.pop("specification", None)
        extra_images = validated_data.pop("images_upload", [])
        extra_attachments = validated_data.pop("attachments_upload", [])
        tutorial_videos = validated_data.pop("tutorial_videos_upload", [])
        troubleshooting_videos = validated_data.pop("troubleshooting_videos_upload", [])

        if spec_data is not None:
            validated_data["specification"] = spec_data

        instance = DroneImage.objects.create(**validated_data)

        # Extra images
        for img in extra_images:
            DroneExtraImage.objects.create(drone=instance, image=img)

        # Attachments
        for f in extra_attachments:
            DroneAttachment.objects.create(drone=instance, file=f)

        # Tutorial videos
        for f in tutorial_videos:
            DroneTutorialVideo.objects.create(drone=instance, file=f)

        # Troubleshooting videos
        for f in troubleshooting_videos:
            DroneTroubleshootingVideo.objects.create(drone=instance, file=f)

        return instance

    # -------- UPDATE --------
    def update(self, instance, validated_data):
        spec_data = validated_data.pop("specification", None)
        extra_images = validated_data.pop("images_upload", [])
        extra_attachments = validated_data.pop("attachments_upload", [])
        tutorial_videos = validated_data.pop("tutorial_videos_upload", [])
        troubleshooting_videos = validated_data.pop("troubleshooting_videos_upload", [])

        if spec_data is not None:
            instance.specification = spec_data

        # Other fields (name, image, etc.)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Append new extra images
        for img in extra_images:
            DroneExtraImage.objects.create(drone=instance, image=img)

        # Append new attachments
        for f in extra_attachments:
            DroneAttachment.objects.create(drone=instance, file=f)

        # Append new tutorial videos
        for f in tutorial_videos:
            DroneTutorialVideo.objects.create(drone=instance, file=f)

        # Append new troubleshooting videos
        for f in troubleshooting_videos:
            DroneTroubleshootingVideo.objects.create(drone=instance, file=f)

        return instance
