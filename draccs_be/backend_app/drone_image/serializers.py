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


class SpecificationSerializer(serializers.Serializer):
    weight = serializers.CharField(required=False, allow_blank=True)
    dimensions = serializers.CharField(required=False, allow_blank=True)
    speed = serializers.CharField(required=False, allow_blank=True)
    takeoff_altitude = serializers.CharField(required=False, allow_blank=True)
    flight_time = serializers.CharField(required=False, allow_blank=True)
    flight_distance = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=False,                   # keep line breaks/spacing
        style={"base_template": "textarea.html"} # nice textarea in browsable API
    )

    def to_internal_value(self, data):
        """
        Allow `specification` to be sent as:
        - a JSON object, OR
        - a JSON string in form-data, e.g.:
          {"weight": "5 kg", "description": "Long multi-line text..."}
        """
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = {}
        return super().to_internal_value(data)


class DroneExtraImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneExtraImage
        fields = ["id", "image"]


class DroneImageSerializer(serializers.ModelSerializer):
    # use the nested specification serializer
    specification = SpecificationSerializer(required=False)

    #  all extra images (what you GET)
    images = DroneExtraImageSerializer(many=True, read_only=True)

    #  multiple images to upload (what you POST/PUT/PATCH)
    new_images = serializers.ListField(
        child=serializers.ImageField(max_length=None, allow_empty_file=False, use_url=True),
        write_only=True,
        required=False,
    )

    class Meta:
        model = DroneImage
        fields = [
            "id",
            "name",
            "image",                # optional main image (single)
            "specification",
            "tutorial_video",
            "troubleshooting_video",
            "images",               # list of extra images (read-only)
            "new_images",           # list of images to upload (write-only)
            "created_at",
        ]

    def create(self, validated_data):
        # spec_data is already a dict from SpecificationSerializer
        spec_data = validated_data.pop("specification", None)
        extra_images = validated_data.pop("new_images", [])

        if spec_data is not None:
            validated_data["specification"] = spec_data

        drone = super().create(validated_data)

        # create extra image rows
        for img in extra_images:
            DroneExtraImage.objects.create(drone=drone, image=img)

        return drone

    def update(self, instance, validated_data):
        # Merge updated specification into existing JSON
        spec_data = validated_data.pop("specification", None)
        extra_images = validated_data.pop("new_images", [])

        if spec_data is not None:
            existing = instance.specification or {}
            existing.update(spec_data)  # only overwrite provided keys
            instance.specification = existing

        # update simple fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # append new images without deleting older ones
        for img in extra_images:
            DroneExtraImage.objects.create(drone=instance, image=img)

        return instance
