from django.db import models

class DroneImage(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="drone_images/")
    specification = models.JSONField(default=dict, blank=True)  # specs JSON

    created_at = models.DateTimeField(auto_now_add=True)  # ✅ must exist

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)
