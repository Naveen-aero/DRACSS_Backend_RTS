from django.db import models

class Account(models.Model):
    CLIENT_TYPES = [
        ("client", "Client"),
        ("bd", "BD Team"),
    ]

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
    address = models.TextField(blank=True)
    client_type = models.CharField(
        max_length=20,
        choices=CLIENT_TYPES,
        null=True,          # can be null in DB
        blank=True,         #  can be left blank in forms
        default=None        #  no default client type
    ) 
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True)

    # store only a hashed password
    password = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.client_type})"
