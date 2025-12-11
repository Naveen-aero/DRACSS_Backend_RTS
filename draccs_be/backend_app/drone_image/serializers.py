# from rest_framework import serializers
# from .models import DroneImage, DroneExtraImage
# import json


# # -------- SPECIFICATION SERIALIZER ----------
# class SpecificationSerializer(serializers.Serializer):
#     weight = serializers.CharField(required=False, allow_blank=True)
#     dimensions = serializers.CharField(required=False, allow_blank=True)
#     speed = serializers.CharField(required=False, allow_blank=True)
#     takeoff_altitude = serializers.CharField(required=False, allow_blank=True)
#     flight_time = serializers.CharField(required=False, allow_blank=True)
#     flight_distance = serializers.CharField(required=False, allow_blank=True)

#     def to_internal_value(self, data):
#         # Allow specification to be sent as JSON string in form-data
#         if isinstance(data, str):
#             try:
#                 data = json.loads(data)
#             except json.JSONDecodeError:
#                 data = {}
#         return super().to_internal_value(data)


# # -------- EXTRA IMAGES SERIALIZER ----------
# class DroneExtraImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DroneExtraImage
#         fields = ["id", "image"]   # id is important for per-image delete


# # -------- MAIN DRONE SERIALIZER ----------
# class DroneImageSerializer(serializers.ModelSerializer):
#     specification = SpecificationSerializer(required=False)
#     images = DroneExtraImageSerializer(many=True, read_only=True)

#     # For POST/PATCH: multiple extra images
#     images_upload = serializers.ListField(
#         child=serializers.ImageField(),
#         write_only=True,
#         required=False,
#     )

#     images_delete = serializers.ListField(
#         child=serializers.IntegerField(),
#         write_only=True,
#         required=False,
#         help_text="IDs of DroneExtraImage to delete",
#     )

#     class Meta:
#         model = DroneImage
#         fields = [
#             "id",
#             "name",
#             "image",                # main image (single)
#             "specification",
#             "tutorial_video",
#             "troubleshooting_video",
#             "images",               # read-only extra images list
#             "images_upload",        # write-only list for upload
#             "images_delete", 
#             "created_at",
#         ]

#     def to_internal_value(self, data):
#         """
#         Normalize React FormData keys:
#         - If frontend sends images_upload[] instead of images_upload,
#           remap it so DRF ListField sees the correct key.
#         """
#         if hasattr(data, "getlist") and "images_upload[]" in data:
#             data = data.copy()  # QueryDict is immutable by default
#             data.setlist("images_upload", data.getlist("images_upload[]"))
#         if "images_delete[]" in data:
#                 data.setlist("images_delete", data.getlist("images_delete[]"))
#         return super().to_internal_value(data)

#     # -------- CREATE --------
#     def create(self, validated_data):
#         spec_data = validated_data.pop("specification", None)
#         extra_images = validated_data.pop("images_upload", [])
#         validated_data.pop("images_delete", None)

#         # spec_data is already a dict thanks to SpecificationSerializer
#         if spec_data is not None:
#             validated_data["specification"] = spec_data

#         instance = DroneImage.objects.create(**validated_data)

#         # Save extra images
#         for img in extra_images:
#             DroneExtraImage.objects.create(drone=instance, image=img)

#         return instance

#     # -------- UPDATE --------
#     def update(self, instance, validated_data):
#         spec_data = validated_data.pop("specification", None)
#         extra_images = validated_data.pop("images_upload", [])
#         images_to_delete = validated_data.pop("images_delete", [])

#         # Overwrite specification completely with new dict
#         if spec_data is not None:
#             # Already dict from SpecificationSerializer, no need for json.loads
#             instance.specification = spec_data

#         # Update other simple fields
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         instance.save()

#         for img_id in images_to_delete:
#             try:
#                 img_obj = instance.images.get(id=img_id)
#                 img_obj.delete()  # removes file + DB record
#             except DroneExtraImage.DoesNotExist:
#                 pass

#         # Append new extra images (existing ones remain)
#         for img in extra_images:
#             DroneExtraImage.objects.create(drone=instance, image=img)

#         return instance


from rest_framework import serializers
from .models import (
    DroneImage,
    DroneExtraImage,
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
        # Allow specification to be sent as JSON string in form-data
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
        fields = ["id", "image"]   # id is important for per-image delete


# -------- VIDEO SERIALIZERS ----------
class DroneTutorialVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneTutorialVideo
        fields = ["id", "video"]


class DroneTroubleshootingVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneTroubleshootingVideo
        fields = ["id", "video"]


# -------- MAIN DRONE SERIALIZER ----------
class DroneImageSerializer(serializers.ModelSerializer):
    specification = SpecificationSerializer(required=False)

    images = DroneExtraImageSerializer(many=True, read_only=True)
    tutorial_videos = DroneTutorialVideoSerializer(many=True, read_only=True)
    troubleshooting_videos = DroneTroubleshootingVideoSerializer(
        many=True, read_only=True
    )

    # For POST/PATCH: multiple extra images
    images_upload = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )

    # For POST/PATCH: multiple tutorial videos
    tutorial_videos_upload = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
    )

    # For POST/PATCH: multiple troubleshooting videos
    troubleshooting_videos_upload = serializers.ListField(
        child=serializers.FileField(),
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
            # arrays of videos:
            "tutorial_videos",
            "tutorial_videos_upload",
            "troubleshooting_videos",
            "troubleshooting_videos_upload",
            # extra images:
            "images",
            "images_upload",
            "created_at",
        ]

    def to_internal_value(self, data):
        """
        Normalize React FormData keys:
        - If frontend sends images_upload[] instead of images_upload
        - Same for tutorial_videos_upload[] and troubleshooting_videos_upload[]
        """
        if hasattr(data, "getlist"):
            data = data.copy()  # QueryDict is immutable by default

            if "images_upload[]" in data:
                data.setlist("images_upload", data.getlist("images_upload[]"))

            if "tutorial_videos_upload[]" in data:
                data.setlist(
                    "tutorial_videos_upload",
                    data.getlist("tutorial_videos_upload[]"),
                )

            if "troubleshooting_videos_upload[]" in data:
                data.setlist(
                    "troubleshooting_videos_upload",
                    data.getlist("troubleshooting_videos_upload[]"),
                )

        return super().to_internal_value(data)

    # -------- CREATE --------
    def create(self, validated_data):
        spec_data = validated_data.pop("specification", None)
        extra_images = validated_data.pop("images_upload", [])
        tutorial_videos = validated_data.pop("tutorial_videos_upload", [])
        troubleshooting_videos = validated_data.pop(
            "troubleshooting_videos_upload", []
        )

        # spec_data is already a dict thanks to SpecificationSerializer
        if spec_data is not None:
            validated_data["specification"] = spec_data

        instance = DroneImage.objects.create(**validated_data)

        # Save extra images
        for img in extra_images:
            DroneExtraImage.objects.create(drone=instance, image=img)

        # Save tutorial videos
        for vid in tutorial_videos:
            DroneTutorialVideo.objects.create(drone=instance, video=vid)

        # Save troubleshooting videos
        for vid in troubleshooting_videos:
            DroneTroubleshootingVideo.objects.create(drone=instance, video=vid)

        return instance

    # -------- UPDATE --------
    def update(self, instance, validated_data):
        spec_data = validated_data.pop("specification", None)
        extra_images = validated_data.pop("images_upload", [])
        tutorial_videos = validated_data.pop("tutorial_videos_upload", [])
        troubleshooting_videos = validated_data.pop(
            "troubleshooting_videos_upload", []
        )

        # Overwrite specification completely with new dict
        if spec_data is not None:
            instance.specification = spec_data

        # Update other simple fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Append new extra images (existing ones remain)
        for img in extra_images:
            DroneExtraImage.objects.create(drone=instance, image=img)

        # Append new tutorial videos
        for vid in tutorial_videos:
            DroneTutorialVideo.objects.create(drone=instance, video=vid)

        # Append new troubleshooting videos
        for vid in troubleshooting_videos:
            DroneTroubleshootingVideo.objects.create(drone=instance, video=vid)

        return instance
