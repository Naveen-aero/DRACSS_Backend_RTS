# backend_app/orderform/models.py

from django.db import models
from django.utils import timezone


def today_local():
    # Returns local date (no time part), DRF-friendly
    return timezone.localdate()


# ---------- LEGACY HELPERS FOR OLD MIGRATIONS (0005) ----------

def manufacturer_upload_to(instance, filename):
    """
    OLD helper used in migration 0005_orderdeliveryinfo.
    Even though we no longer use this in the current models,
    the migration still imports it, so it MUST exist.
    """
    try:
        order_number = instance.order.order_number
    except AttributeError:
        order_number = "UNKNOWN"
    return f"orders/{order_number}/manufacturer/{filename}"


def testing_upload_to(instance, filename):
    """
    OLD helper used in migration 0005_orderdeliveryinfo.
    """
    try:
        order_number = instance.order.order_number
    except AttributeError:
        order_number = "UNKNOWN"
    return f"orders/{order_number}/testing/{filename}"


# --------------------------------------------------------------


class ChecklistItem(models.Model):
    CATEGORY_CHOICES = [
        ("STANDARD_KIT", "Standard Kit"),
        ("PAYLOAD", "Payload"),
        ("GCS", "Ground Control Station"),
        ("ACCESSORIES", "Accessories"),
        ("SOFTWARE", "Software"),
        ("FIELD_TRAINING", "Field Training"),
        ("RPC_PROGRAM", "RPC Program"),
    ]

    drone_model = models.CharField(max_length=100, default="Bhumi A10E")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=255)
    default_quantity = models.PositiveIntegerField(default=1)
    is_mandatory = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.drone_model} - {self.get_category_display()} - {self.description}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("CONFIRMED", "Confirmed"),
        ("DISPATCHED", "Dispatched"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]

    order_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)

    billing_address = models.TextField(blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)

    drone_model = models.CharField(max_length=100, default="Bhumi A10E")

    # Fixed: use a pure date, not datetime
    order_date = models.DateField(default=today_local)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            last = Order.objects.order_by("-id").first()
            if last and last.order_number.startswith("ORD_"):
                try:
                    last_num = int(last.order_number.split("_")[1])
                except (IndexError, ValueError):
                    last_num = 0
            else:
                last_num = 0
            self.order_number = f"ORD_{last_num + 1:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)

    checklist_item = models.ForeignKey(
        ChecklistItem,
        related_name="order_items",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    description = models.CharField(max_length=255)
    quantity_ordered = models.PositiveIntegerField(default=1)
    quantity_delivered = models.PositiveIntegerField(default=0)
    is_checked = models.BooleanField(default=False)
    is_from_template = models.BooleanField(default=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.description}"


# ================== NEW / CHANGED CODE STARTS HERE ==================


class OrderDeliveryInfo(models.Model):
    """
    Extra per-order information:

    - UIN registration number
    - Ready for delivery flag

    Attachments (manufacturer/testing) are stored in a separate table:
    OrderDeliveryAttachment (many rows per order).
    """

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="delivery_info",   # access via order.delivery_info
        primary_key=True,
    )

    uin_registration_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    # This is your "Ready for delivery" flag
    ready_for_delivery = models.BooleanField(default=False)

    def __str__(self):
        return f"Delivery info for {self.order.order_number}"


def delivery_attachment_upload_to(instance, filename):
    """
    File path for all delivery attachments, grouped by order_number and type.

    Example:
      orders/ORD_00004/manufacturer/<file>
      orders/ORD_00004/testing/<file>
    """
    order_number = instance.delivery_info.order.order_number
    folder = instance.attachment_type.lower()  # "manufacturer" or "testing"
    return f"orders/{order_number}/{folder}/{filename}"


class OrderDeliveryAttachment(models.Model):
    """
    Multiple attachments per order delivery info.

    - attachment_type = "MANUFACTURER" or "TESTING"
    - file = the uploaded document
    """

    ATTACHMENT_TYPE_CHOICES = [
        ("MANUFACTURER", "Manufacturer"),
        ("TESTING", "Testing"),
    ]

    delivery_info = models.ForeignKey(
        OrderDeliveryInfo,
        related_name="attachments",
        on_delete=models.CASCADE,
    )

    attachment_type = models.CharField(
        max_length=20,
        choices=ATTACHMENT_TYPE_CHOICES,
    )

    file = models.FileField(upload_to=delivery_attachment_upload_to)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.delivery_info.order.order_number} - {self.attachment_type} - {self.file.name}"
