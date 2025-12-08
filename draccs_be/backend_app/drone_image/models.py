from django.db import models

class DroneImage(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="drone_images/")

    #  Specifications stored as JSON (you already added this)
    specification = models.JSONField(default=dict, blank=True)

    #  NEW: video fields
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

    # ensure files are removed from disk when deleting
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        if self.tutorial_video:
            self.tutorial_video.delete(save=False)
        if self.troubleshooting_video:
            self.troubleshooting_video.delete(save=False)
        super().delete(*args, **kwargs)
