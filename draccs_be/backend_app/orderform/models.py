from django.db import models
from django.utils import timezone


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

    # This is the drone model this checklist template belongs to
    drone_model = models.CharField(max_length=100, default="Bhumi A10E")

    # This will drive the "Description" column in UI via get_category_display()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    # This will be shown under "BhumiA10E Drone" column (item name)
    description = models.CharField(max_length=255)

    # This is the "Nos" column value
    default_quantity = models.PositiveIntegerField(default=1)

    # For template: whether this line is included by default in the standard checklist
    is_mandatory = models.BooleanField(default=True)

    # For ordering rows in the table
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        # Show human readable category for clarity
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
        max_length=20, unique=True, editable=False
    )

    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)

    billing_address = models.TextField(blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)

    drone_model = models.CharField(max_length=100, default="Bhumi A10E")
    order_date = models.DateField(default=timezone.now)
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

    # Links back to the template row (optional)
    checklist_item = models.ForeignKey(
        ChecklistItem,
        related_name="order_items",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Snapshot of the item name at time of order
    description = models.CharField(max_length=255)

    quantity_ordered = models.PositiveIntegerField(default=1)
    quantity_delivered = models.PositiveIntegerField(default=0)

    # This is the runtime "Checklist" tick per order
    is_checked = models.BooleanField(default=False)

    # True if this row came from the standard template, False if added manually
    is_from_template = models.BooleanField(default=True)

    remarks = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.description}"
