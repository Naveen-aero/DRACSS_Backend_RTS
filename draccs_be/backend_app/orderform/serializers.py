from rest_framework import serializers
from .models import ChecklistItem, Order, OrderItem


# ========= TEMPLATE CHECKLIST SERIALIZER (for /api/checklist-items/) =========
class ChecklistItemSerializer(serializers.ModelSerializer):
    # UI "Description" column (section name)
    description = serializers.SerializerMethodField()

    # UI "BhumiA10E Drone" column (item name)
    bhumi_a10e_drone = serializers.SerializerMethodField()

    # UI "Nos" column
    nos = serializers.IntegerField(source="default_quantity")

    # UI "Checklist" column
    checklist = serializers.BooleanField(source="is_mandatory")

    class Meta:
        model = ChecklistItem
        fields = [
            "id",
            "description",        # e.g. "Standard Kit"
            "bhumi_a10e_drone",   # e.g. "Drone", "Propeller Set (1 CW; 1 CCW)"
            "nos",                # e.g. 1
            "checklist",          # e.g. true
            "sort_order",         # ordering in table
        ]

    def get_description(self, obj):
        """
        Section name for the left column.

        Special rule:
        - The row 'Bhumi A10E Drone' (category 'DRONE') should also show under 'Standard Kit'.
        """
        if obj.category == "DRONE" and obj.description == "Bhumi A10E Drone":
            return "Standard Kit"
        # For TRAINING / SOFTWARE / etc, use their display names
        return obj.get_category_display()

    def get_bhumi_a10e_drone(self, obj):
        """
        Item name for the second column.

        Special rule:
        - For the main drone row, show just 'Drone'.
        """
        if obj.category == "DRONE" and obj.description == "Bhumi A10E Drone":
            return "Drone"
        return obj.description


# ========= ORDER + ORDER ITEMS (WHERE MODIFIED DATA IS STORED) =========

class OrderItemSerializer(serializers.ModelSerializer):
    # Optional: include template info (section, default nos, etc.) for reference
    checklist_item_detail = ChecklistItemSerializer(
        source="checklist_item", read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "checklist_item",        # FK to template (nullable)
            "checklist_item_detail", # read-only template data
            "description",           # snapshot name (can be edited)
            "quantity_ordered",
            "quantity_delivered",
            "is_checked",            # tick per order
            "is_from_template",      # True if cloned from template
            "remarks",
        ]


class OrderSerializer(serializers.ModelSerializer):
    # Nested list of order items
    items = OrderItemSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "customer_name",
            "customer_email",
            "customer_phone",
            "billing_address",
            "shipping_address",
            "drone_model",
            "order_date",
            "status",
            "remarks",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = ["order_number", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        When creating a new order:

        - If 'items' is provided in payload: use those directly.
        - If 'items' is NOT provided: auto-copy all ChecklistItem rows for that drone_model
          into OrderItem table. This becomes the editable checklist instance.
        """
        items_data = validated_data.pop("items", None)

        # Create the order first
        order = Order.objects.create(**validated_data)

        if items_data:
            # Frontend sent custom items (advanced usage)
            for item in items_data:
                OrderItem.objects.create(order=order, **item)
        else:
            # AUTO-COPY from template for this drone model
            drone_model = order.drone_model or "Bhumi A10E"
            template_items = ChecklistItem.objects.filter(
                drone_model=drone_model
            ).order_by("sort_order")

            for tmpl in template_items:
                OrderItem.objects.create(
                    order=order,
                    checklist_item=tmpl,
                    description=tmpl.description,             # snapshot name at order time
                    quantity_ordered=tmpl.default_quantity,   # start from default quantity
                    quantity_delivered=0,
                    is_checked=False,                         # not yet checked
                    is_from_template=True,
                    remarks="",
                )

        return order

    def update(self, instance, validated_data):
        """
        Update order header + optionally replace items.

        - If 'items' is included in payload: we clear existing items and recreate.
          (You can later change this to smarter diff logic if needed.)
        """
        items_data = validated_data.pop("items", None)

        # Update order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # If items provided, replace them
        if items_data is not None:
            instance.items.all().delete()
            for item in items_data:
                OrderItem.objects.create(order=instance, **item)

        return instance
