# from django.db import models

# def drone_attachment_path(instance, filename):
#     uin = instance.uin_number or "no_uin"
#     return f"drone_attachments/{uin}/{filename}"

# def drone_image_path(instance, filename):
#     uin = instance.uin_number or "no_uin"
#     return f"drone_images/{uin}/{filename}"

# class DroneRegistration(models.Model):
#     model_name = models.CharField(max_length=120)
#     drone_type = models.CharField(max_length=120, blank=True)
#     manufacturer = models.CharField(max_length=120, blank=True)

#     # Often unique identifiers
#     uin_number = models.CharField(max_length=64, unique=True)
#     drone_serial_number = models.CharField(max_length=120, unique=True)
#     drone_id = models.CharField(max_length=64, unique=True, blank=True, null=True)

#     flight_controller_serial_number = models.CharField(max_length=120, blank=True)
#     remote_controller = models.CharField(max_length=120, blank=True)
#     battery_charger_serial_number = models.CharField(max_length=120, blank=True)
#     battery_serial_number_1 = models.CharField(max_length=120, blank=True)
#     battery_serial_number_2 = models.CharField(max_length=120, blank=True)

#     # File uploads
#     attachment = models.FileField(upload_to=drone_attachment_path, blank=True, null=True)
#     image = models.ImageField(upload_to=drone_image_path, blank=True, null=True)

#     client_details = models.JSONField(
#         blank=True,
#         null=True,
#         default=list,
#         help_text=(
#             "Optional list of client entries with keys: "
#             "model_name, uin_number, drone_serial_number, "
#             "flight_controller_serial_number, remote_controller, "
#             "battery_charger_serial_number, battery_serial_number_1, "
#             "battery_serial_number_2, drone_type, attachment"
#         ),
#     )

#     # Flags
#     registered = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)

#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.model_name} / {self.uin_number}"


from django.db import models


def drone_attachment_path(instance, filename):
    uin = instance.uin_number or "no_uin"
    return f"drone_attachments/{uin}/{filename}"


def drone_image_path(instance, filename):
    uin = instance.uin_number or "no_uin"
    return f"drone_images/{uin}/{filename}"


class DroneRegistration(models.Model):
    model_name = models.CharField(max_length=120)
    drone_type = models.CharField(max_length=120, blank=True)
    manufacturer = models.CharField(max_length=120, blank=True)

    # Often unique identifiers
    uin_number = models.CharField(max_length=64, unique=True)
    drone_serial_number = models.CharField(max_length=120, unique=True)
    drone_id = models.CharField(max_length=64, unique=True, blank=True, null=True)

    flight_controller_serial_number = models.CharField(max_length=120, blank=True)
    remote_controller = models.CharField(max_length=120, blank=True)
    battery_charger_serial_number = models.CharField(max_length=120, blank=True)
    battery_serial_number_1 = models.CharField(max_length=120, blank=True)
    battery_serial_number_2 = models.CharField(max_length=120, blank=True)

    # File uploads
    attachment = models.FileField(upload_to=drone_attachment_path, blank=True, null=True)
    image = models.ImageField(upload_to=drone_image_path, blank=True, null=True)

    client_details = models.JSONField(
        blank=True,
        null=True,
        default=list,
        help_text=(
            "Optional list of client entries with keys: "
            "model_name, uin_number, drone_serial_number, "
            "flight_controller_serial_number, remote_controller, "
            "battery_charger_serial_number, battery_serial_number_1, "
            "battery_serial_number_2, drone_type, attachment"
        ),
    )

    #  registered: tri-state: None (not decided), True, False
    registered = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="None = not decided yet, True = registered, False = not registered",
    )

    #  remarks (mandatory when registered == False OR is_active == False — enforce in serializer)
    remarks = models.TextField(
        null=True,
        blank=True,
        help_text="Mandatory if registered is False (and also when is_active is False, as per serializer rule)",
    )

    # CHANGED: is_active is now tri-state (None first)
    is_active = models.BooleanField(
        null=True,
        blank=True,
        default=None,
        help_text="None = not decided yet, True = active, False = inactive",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.model_name} / {self.uin_number}"
