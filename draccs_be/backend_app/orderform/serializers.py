from rest_framework import serializers
from .models import ChecklistItem, Order, OrderItem


class ChecklistItemSerializer(serializers.ModelSerializer):
    # UI "Description" column: section name (Standard Kit, Payload, ...)
    description = serializers.SerializerMethodField()

    # UI "BhumiA10E Drone" column: actual item name
    bhumi_a10e_drone = serializers.CharField(source="description")

    # UI "Nos" column: quantity
    nos = serializers.IntegerField(source="default_quantity")

    # UI "Checklist" column: tick
    checklist = serializers.BooleanField(source="is_mandatory")

    class Meta:
        model = ChecklistItem
        fields = [
            "id",
            "description",        # ex: "Standard Kit"
            "bhumi_a10e_drone",   # ex: "Bhumi A10E Drone"
            "nos",                # ex: 1
            "checklist",          # ex: true
            "sort_order",         # ex: 1
        ]

    def get_description(self, obj):
        # Converts "STANDARD_KIT" -> "Standard Kit", "PAYLOAD" -> "Payload", etc.
        return obj.get_category_display()


class OrderItemSerializer(serializers.ModelSerializer):
    checklist_item_detail = ChecklistItemSerializer(
        source="checklist_item", read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "checklist_item",
            "checklist_item_detail",
            "description",
            "quantity_ordered",
            "quantity_delivered",
            "is_checked",
            "is_from_template",
            "remarks",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

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
        items_data = validated_data.pop("items", [])
        order = Order.objects.create(**validated_data)
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item in items_data:
                OrderItem.objects.create(order=instance, **item)

        return instance
