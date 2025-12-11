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

#     class Meta:  #  add this
#         db_table = "drone_image_droneextraimage"


from django.db import models


class DroneImage(models.Model):
    name = models.CharField(max_length=255)

    # Optional "main" image
    image = models.ImageField(
        upload_to="drone_images/",
        blank=True,
        null=True,
    )

    # Specifications stored as JSON
    specification = models.JSONField(default=dict, blank=True)

    # OLD single video fields (you can keep these if you want backward compatibility,
    # but we will NOT expose them in the serializer anymore)
    tutorial_video = models.FileField(
        upload_to="drone_videos/tutorials/",
        blank=True,
        null=True,
    )
    troubleshooting_video = models.FileField(
        upload_to="drone_videos/troubleshooting/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    # ensure files are removed from disk when deleting the whole drone
    def delete(self, *args, **kwargs):
        # delete main image
        if self.image:
            self.image.delete(save=False)
        # delete videos
        if self.tutorial_video:
            self.tutorial_video.delete(save=False)
        if self.troubleshooting_video:
            self.troubleshooting_video.delete(save=False)
        # delete all extra images
        for img in self.images.all():
            if img.image:
                img.image.delete(save=False)
        # delete all tutorial videos
        for vid in self.tutorial_videos.all():
            if vid.video:
                vid.video.delete(save=False)
        # delete all troubleshooting videos
        for vid in self.troubleshooting_videos.all():
            if vid.video:
                vid.video.delete(save=False)

        super().delete(*args, **kwargs)

    class Meta:
        db_table = "drone_image_droneimage"


class DroneExtraImage(models.Model):
    """
    Extra images for a DroneImage (one DroneImage -> many DroneExtraImage)
    """
    drone = models.ForeignKey(
        DroneImage,
        related_name="images",          # access via drone.images.all()
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to="drone_images/multiple/")

    def __str__(self):
        return f"{self.drone.name} - extra image {self.id}"

    # allow deleting a single extra image (file + DB row)
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)  # remove file from /media/...
        super().delete(*args, **kwargs)

    class Meta:
        db_table = "drone_image_droneextraimage"


class DroneTutorialVideo(models.Model):
    """
    Multiple tutorial videos for a DroneImage
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

    class Meta:
        db_table = "drone_image_dronetutorialvideo"


class DroneTroubleshootingVideo(models.Model):
    """
    Multiple troubleshooting videos for a DroneImage
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

    class Meta:
        db_table = "drone_image_dronetroubleshootingvideo"
