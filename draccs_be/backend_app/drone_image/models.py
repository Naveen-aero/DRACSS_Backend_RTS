# from django.db import models


# class DroneImage(models.Model):
#     name = models.CharField(max_length=255)

#     # Optional "main" image (you can keep or later remove this)
#     image = models.ImageField(
#         upload_to="drone_images/",
#         blank=True,
#         null=True,
#     )

#     # Specifications stored as JSON
#     specification = models.JSONField(default=dict, blank=True)

#     # Video fields
#     tutorial_video = models.FileField(
#         upload_to="drone_videos/tutorials/",
#         blank=True,
#         null=True,
#     )
#     troubleshooting_video = models.FileField(
#         upload_to="drone_videos/troubleshooting/",
#         blank=True,
#         null=True,
#     )

#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name

#     # ensure files are removed from disk when deleting the whole drone
#     def delete(self, *args, **kwargs):
#         # delete main image
#         if self.image:
#             self.image.delete(save=False)
#         # delete videos
#         if self.tutorial_video:
#             self.tutorial_video.delete(save=False)
#         if self.troubleshooting_video:
#             self.troubleshooting_video.delete(save=False)
#         # delete all extra images
#         for img in self.images.all():
#             if img.image:
#                 img.image.delete(save=False)
#         super().delete(*args, **kwargs)


# class DroneExtraImage(models.Model):
#     """
#     Extra images for a DroneImage (one DroneImage -> many DroneExtraImage)
#     """
#     drone = models.ForeignKey(
#         DroneImage,
#         related_name="images",          # access via drone.images.all()
#         on_delete=models.CASCADE,
#     )
#     image = models.ImageField(upload_to="drone_images/multiple/")

#     def __str__(self):
#         return f"{self.drone.name} - extra image {self.id}"

#     # allow deleting a single extra image (file + DB row)
#     def delete(self, *args, **kwargs):
#         if self.image:
#             self.image.delete(save=False)  # remove file from /media/...
#         super().delete(*args, **kwargs)

from django.db import models


class DroneImage(models.Model):
    name = models.CharField(max_length=255)

    # Optional main image
    image = models.ImageField(
        upload_to="drone_images/",
        blank=True,
        null=True,
    )

    # Specifications stored as JSON
    specification = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # delete main image
        if self.image:
            self.image.delete(save=False)
        # cascade will delete related rows; their delete() will remove files
        super().delete(*args, **kwargs)


class DroneExtraImage(models.Model):
    """
    Extra images for a DroneImage (one DroneImage -> many extra images)
    """
    drone = models.ForeignKey(
        DroneImage,
        related_name="images",      # appears as "images": [] in DroneImageSerializer
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to="drone_images/multiple/")

    def __str__(self):
        return f"{self.drone.name} - extra image {self.id}"

    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)


class DroneAttachment(models.Model):
    """
    Generic file attachments for a DroneImage
    """
    drone = models.ForeignKey(
        DroneImage,
        related_name="attachments",
        on_delete=models.CASCADE,
    )
    file = models.FileField(upload_to="drone_attachments/")

    def __str__(self):
        return f"{self.drone.name} - attachment {self.id}"

    def delete(self, *args, **kwargs):
        if self.file:
            self.file.delete(save=False)
        super().delete(*args, **kwargs)


class DroneTutorialVideo(models.Model):
    """
    Tutorial videos for a DroneImage
    """
    drone = models.ForeignKey(
        DroneImage,
        related_name="tutorial_videos",
        on_delete=models.CASCADE,
    )
    video = models.FileField(upload_to="drone_videos/tutorials/")

    def __str__(self):
        return f"{self.drone.name} - tutorial video {self.id}"

    def delete(self, *args, **kwargs):
        if self.video:
            self.video.delete(save=False)
        super().delete(*args, **kwargs)


class DroneTroubleshootingVideo(models.Model):
    """
    Troubleshooting videos for a DroneImage
    """
    drone = models.ForeignKey(
        DroneImage,
        related_name="troubleshooting_videos",
        on_delete=models.CASCADE,
    )
    video = models.FileField(upload_to="drone_videos/troubleshooting/")

    def __str__(self):
        return f"{self.drone.name} - troubleshooting video {self.id}"

    def delete(self, *args, **kwargs):
        if self.video:
            self.video.delete(save=False)
        super().delete(*args, **kwargs)
