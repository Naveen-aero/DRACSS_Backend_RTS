# from rest_framework import generics
# from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# from .models import DroneImage, DroneExtraImage
# from .serializers import DroneImageSerializer, DroneExtraImageSerializer


# class DroneImageListCreateView(generics.ListCreateAPIView):
#     """
#     GET  /api/drone_images/      -> list all drone images
#     POST /api/drone_images/      -> create new drone image
#     """
#     queryset = DroneImage.objects.all()
#     serializer_class = DroneImageSerializer
#     parser_classes = [MultiPartParser, FormParser, JSONParser]


# class DroneImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
#     """
#     GET    /api/drone_images/<id>/ -> retrieve one
#     PUT    /api/drone_images/<id>/ -> full update
#     PATCH  /api/drone_images/<id>/ -> partial update
#     DELETE /api/drone_images/<id>/ -> delete record + all files
#     """
#     queryset = DroneImage.objects.all()
#     serializer_class = DroneImageSerializer
#     parser_classes = [MultiPartParser, FormParser, JSONParser]


# class DroneExtraImageDestroyView(generics.DestroyAPIView):
#     """
#     DELETE /api/drone_images/<drone_pk>/images/<pk>/
#     -> delete a single extra image that belongs to that drone
#     """
#     serializer_class = DroneExtraImageSerializer

#     def get_queryset(self):
#         # Only allow deleting images attached to this specific drone
#         drone_id = self.kwargs["drone_pk"]
#         return DroneExtraImage.objects.filter(drone_id=drone_id)

from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.conf import settings

from .models import (
    DroneImage,
    DroneExtraImage,
    DroneAttachment,
    DroneTutorialVideo,
    DroneTroubleshootingVideo,
)
from .serializers import (
    DroneImageSerializer,
    DroneExtraImageSerializer,
    DroneAttachmentSerializer,
    DroneTutorialVideoSerializer,
    DroneTroubleshootingVideoSerializer,
)


def _get_files(request, base_key: str):
    """
    Helper to support both:
    - attachments_upload
    - attachments_upload[]
    - same for images_upload, tutorial_videos_upload, troubleshooting_videos_upload
    """
    files = []
    files.extend(request.FILES.getlist(base_key))
    files.extend(request.FILES.getlist(base_key + "[]"))
    return files


def handle_uploads(request, instance: DroneImage):
    """
    Attach uploaded files to the given DroneImage instance.

    Expected field names in multipart/form-data:
    - images_upload or images_upload[]
    - attachments_upload or attachments_upload[]
    - tutorial_videos_upload or tutorial_videos_upload[]
    - troubleshooting_videos_upload or troubleshooting_videos_upload[]
    """

    # Extra images
    for f in _get_files(request, "images_upload"):
        DroneExtraImage.objects.create(drone=instance, image=f)

    # Attachments
    for f in _get_files(request, "attachments_upload"):
        DroneAttachment.objects.create(drone=instance, file=f)

    # Tutorial videos
    for f in _get_files(request, "tutorial_videos_upload"):
        DroneTutorialVideo.objects.create(drone=instance, file=f)

    # Troubleshooting videos
    for f in _get_files(request, "troubleshooting_videos_upload"):
        DroneTroubleshootingVideo.objects.create(drone=instance, file=f)


def _extract_media_path(file_value: str) -> str:
    """
    Convert something like:
    http://127.0.0.1:8000/media/drone_attachments/file.csv
    into:
    drone_attachments/file.csv
    """
    if not isinstance(file_value, str):
        return file_value

    media_url = getattr(settings, "MEDIA_URL", "/media/")
    if media_url and file_value.startswith(media_url):
        return file_value[len(media_url):]

    if "/media/" in file_value:
        return file_value.split("/media/", 1)[1]

    return file_value  # already relative path


class DroneImageListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/drone_images/       -> list
    POST /api/drone_images/       -> create + optional uploads + optional JSON attachments
    """
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):
        # Strip upload fields (with and without [])
        data = request.data.copy()
        for key in [
            "images_upload",
            "images_upload[]",
            "attachments_upload",
            "attachments_upload[]",
            "tutorial_videos_upload",
            "tutorial_videos_upload[]",
            "troubleshooting_videos_upload",
            "troubleshooting_videos_upload[]",
        ]:
            if key in data:
                data.pop(key)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # Handle file uploads (multipart)
        handle_uploads(request, instance)

        # Handle JSON attachments (if someone sends attachments in JSON on create)
        attachments_data = request.data.get("attachments")
        if isinstance(attachments_data, list):
            # clear existing just in case
            instance.attachments.all().delete()
            for att in attachments_data:
                file_val = att.get("file")
                if not file_val:
                    continue
                rel = _extract_media_path(file_val)
                DroneAttachment.objects.create(drone=instance, file=rel)

        out = self.get_serializer(instance)
        headers = self.get_success_headers(out.data)
        return Response(out.data, status=status.HTTP_201_CREATED, headers=headers)


class DroneImageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/drone_images/<id>/
    PUT    /api/drone_images/<id>/
    PATCH  /api/drone_images/<id>/  -> update + append uploads + handle JSON attachments
    DELETE /api/drone_images/<id>/
    """
    queryset = DroneImage.objects.all()
    serializer_class = DroneImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def patch(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()

        # 1) Normal fields through serializer
        data = request.data.copy()
        for key in [
            "images_upload",
            "images_upload[]",
            "attachments_upload",
            "attachments_upload[]",
            "tutorial_videos_upload",
            "tutorial_videos_upload[]",
            "troubleshooting_videos_upload",
            "troubleshooting_videos_upload[]",
        ]:
            if key in data:
                data.pop(key)

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # 2) File uploads (multipart)
        handle_uploads(request, instance)

        # 3) JSON attachments (your case)
        attachments_data = request.data.get("attachments")
        if isinstance(attachments_data, list):
            # replace existing attachments with those from JSON
            instance.attachments.all().delete()
            for att in attachments_data:
                file_val = att.get("file")
                if not file_val:
                    continue
                rel = _extract_media_path(file_val)
                DroneAttachment.objects.create(drone=instance, file=rel)

        out = self.get_serializer(instance)
        return Response(out.data, status=status.HTTP_200_OK)


class DroneExtraImageDestroyView(generics.DestroyAPIView):
    """
    DELETE /api/drone_images/<drone_pk>/images/<pk>/
    -> delete a single extra image
    """
    serializer_class = DroneExtraImageSerializer
    lookup_field = "pk"

    def get_queryset(self):
        drone_id = self.kwargs["drone_pk"]
        return DroneExtraImage.objects.filter(drone_id=drone_id)


class DroneAttachmentDestroyView(generics.DestroyAPIView):
    """
    DELETE /api/drone_images/<drone_pk>/attachments/<pk>/
    -> delete a single attachment
    """
    serializer_class = DroneAttachmentSerializer
    lookup_field = "pk"

    def get_queryset(self):
        drone_id = self.kwargs["drone_pk"]
        return DroneAttachment.objects.filter(drone_id=drone_id)


class DroneTutorialVideoDestroyView(generics.DestroyAPIView):
    """
    DELETE /api/drone_images/<drone_pk>/tutorial_videos/<pk>/
    -> delete a single tutorial video
    """
    serializer_class = DroneTutorialVideoSerializer
    lookup_field = "pk"

    def get_queryset(self):
        drone_id = self.kwargs["drone_pk"]
        return DroneTutorialVideo.objects.filter(drone_id=drone_id)


class DroneTroubleshootingVideoDestroyView(generics.DestroyAPIView):
    """
    DELETE /api/drone_images/<drone_pk>/troubleshooting_videos/<pk>/
    -> delete a single troubleshooting video
    """
    serializer_class = DroneTroubleshootingVideoSerializer
    lookup_field = "pk"

    def get_queryset(self):
        drone_id = self.kwargs["drone_pk"]
        return DroneTroubleshootingVideo.objects.filter(drone_id=drone_id)
