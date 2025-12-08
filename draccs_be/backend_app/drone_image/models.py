from django.db import models

class DroneImage(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="drone_images/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    #  When deleting the model, also delete the file from storage
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete(save=False)  # deletes the file from MEDIA_ROOT
        super().delete(*args, **kwargs)
