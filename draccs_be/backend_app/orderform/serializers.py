from rest_framework import serializers
from .models import ChecklistItem, Order, OrderItem, OrderDeliveryInfo
#                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                            IMPORTANT: import OrderDeliveryInfo


class ChecklistItemSerializer(serializers.ModelSerializer):
    category_label = serializers.CharField(
        source="get_category_display", read_only=True
    )

    class Meta:
        model = ChecklistItem
        fields = [
            "id",
            "drone_model",
            "category",
            "category_label",
            "description",
            "default_quantity",
            "is_mandatory",
            "sort_order",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    # We keep a link to the original template row (optional)
    checklist_item_id = serializers.PrimaryKeyRelatedField(
        source="checklist_item",
        queryset=ChecklistItem.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "checklist_item_id",
            "description",
            "quantity_ordered",
            "quantity_delivered",
            "is_checked",
            "is_from_template",
            "remarks",
        ]


# ============ NEW: OrderDeliveryInfoSerializer ============

class OrderDeliveryInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for:
      - manufacturer_attachment
      - testing_attachment
      - uin_registration_number
      - ready_for_delivery
    linked 1:1 with an Order.
    """

    class Meta:
        model = OrderDeliveryInfo
        fields = [
            "order",                    # order id (PK, same as Order.id)
            "manufacturer_attachment",
            "testing_attachment",
            "uin_registration_number",
            "ready_for_delivery",
        ]
        # Usually we don’t let frontend change 'order' from here
        read_only_fields = ["order"]


# ================== EXISTING OrderSerializer ==================

class OrderSerializer(serializers.ModelSerializer):
    # Editable per-order checklist
    items = OrderItemSerializer(many=True, required=False)

    # NEW: nested read-only delivery info block
    delivery_info = OrderDeliveryInfoSerializer(read_only=True)

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
            "items",          # existing
            "delivery_info",  # NEW field
        ]
        read_only_fields = ["order_number", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        If 'items' is provided in the payload, use that.
        If not, auto-generate OrderItem rows from ChecklistItem
        for the given drone_model (standard checklist).
        """
        items_data = validated_data.pop("items", None)
        order = Order.objects.create(**validated_data)

        if items_data:
            # Frontend sent custom items
            for item_data in items_data:
                OrderItem.objects.create(order=order, **item_data)
        else:
            # Auto-populate from standard checklist for this drone model
            template_items = ChecklistItem.objects.filter(
                drone_model=order.drone_model
            ).order_by("sort_order")

            for tmpl in template_items:
                OrderItem.objects.create(
                    order=order,
                    checklist_item=tmpl,
                    description=tmpl.description,
                    quantity_ordered=tmpl.default_quantity,
                    quantity_delivered=0,
                    is_checked=False,
                    is_from_template=True,
                    remarks="",
                )

        return order

    def update(self, instance, validated_data):
        """
        - Update basic order fields
        - If 'items' is sent, replace the existing items with the new list
          (this makes add/delete/edit very simple from React).
        """
        items_data = validated_data.pop("items", None)

        # Update order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Replace items if provided
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)

        return instance
