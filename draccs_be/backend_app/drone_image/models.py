# drone_registration/models.py
from django.db import models

class DroneImage(models.Model):
    name = models.CharField(max_length=255)  # drone name or image name
    image = models.ImageField(upload_to='drone_images/')  # saved in MEDIA_ROOT/drone_images/

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
