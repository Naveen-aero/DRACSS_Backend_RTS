# from django.db import models
# from django.conf import settings


# def support_attachment_path(instance, filename):
#     return f"support/thread_{instance.thread_id}/{filename}"


# class SupportThread(models.Model):
#     STATUS_CHOICES = [
#         ("OPEN", "Open"),
#         ("IN_PROGRESS", "In Progress"),
#         ("CLOSED", "Closed"),
#     ]

#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="support_threads"
#     )

#     assigned_to = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="assigned_support_threads"
#     )

#     subject = models.CharField(max_length=200)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN")

#     # Optional link to drone registration
#     drone = models.ForeignKey(
#         "drone_registration.DroneRegistration",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True
#     )

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["-updated_at"]

#     def __str__(self):
#         return f"{self.subject} ({self.status})"


# class SupportMessage(models.Model):
#     thread = models.ForeignKey(SupportThread, on_delete=models.CASCADE, related_name="messages")
#     sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

#     message = models.TextField(blank=True)
#     attachment = models.FileField(upload_to=support_attachment_path, null=True, blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["created_at"]
