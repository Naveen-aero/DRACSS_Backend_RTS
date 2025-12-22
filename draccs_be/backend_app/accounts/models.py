# from django.db import models

# class Account(models.Model):
#     CLIENT_TYPES = [
#         ("client", "Client"),
#         ("bd", "BD Team"),
#     ]

#     name = models.CharField(max_length=120)
#     phone = models.CharField(max_length=20, blank=True)
#     email = models.EmailField(unique=True)
#     address = models.TextField(blank=True)
#     client_type = models.CharField(
#         max_length=20,
#         choices=CLIENT_TYPES,
#         null=True,          # can be null in DB
#         blank=True,         #  can be left blank in forms
#         default=None        #  no default client type
#     ) 
#     employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
#     designation = models.CharField(max_length=100, blank=True)

#     # store only a hashed password
#     password = models.CharField(max_length=128)

#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.name} ({self.client_type})"





from django.db import models

class Account(models.Model):
    CLIENT_TYPES = [
        ("client", "Client"),
        ("bd", "BD Team"),
        ("admin", "Admin"),
        ("technical", "Technical"),
        ("pilot", "Pilot"),
        ("inventory", "Inventory"),
    ]

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
    address = models.TextField(blank=True)

    client_type = models.CharField(
        max_length=20,
        choices=CLIENT_TYPES,
        null=True,
        blank=True
    )

    employee_id = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True
    )

    designation = models.CharField(max_length=100, blank=True)

    #  PLAIN PASSWORD (AS YOU REQUESTED)
    password = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        # Auto-generate EMP ID
        if not self.employee_id:
            last = (
                Account.objects
                .filter(employee_id__startswith="EMP")
                .order_by("-employee_id")
                .first()
            )
            if last and last.employee_id:
                num = int(last.employee_id.replace("EMP", ""))
                self.employee_id = f"EMP{num + 1:03d}"
            else:
                self.employee_id = "EMP001"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"
