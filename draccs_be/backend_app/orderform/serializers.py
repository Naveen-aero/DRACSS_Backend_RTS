from rest_framework import serializers
from .models import (
    ChecklistItem,
    Order,
    OrderItem,
    OrderDeliveryInfo,
    OrderDeliveryAttachment,
)


# -------------------------------------------------------------------
# 1) CHECKLIST + ORDER ITEMS
# -------------------------------------------------------------------

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
        #  IMPORTANT: id should be read-only so PATCH/PUT doesn't try to change it
        read_only_fields = ["id"]


# -------------------------------------------------------------------
# 2) ATTACHMENT SERIALIZER (SEPARATE TABLE, USES ORDER ID)
# -------------------------------------------------------------------

class OrderDeliveryAttachmentSerializer(serializers.ModelSerializer):
    """
    One row = one attachment
      - attachment_type: "MANUFACTURER" or "TESTING"
      - file: uploaded document
      - order: Order.id (write-only)
    """

    # You POST using the Order primary key
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        write_only=True,
        help_text="ID of the Order this attachment belongs to",
    )

    # For convenience we also show order_number in responses
    order_number = serializers.CharField(
        source="delivery_info.order.order_number",
        read_only=True,
    )

    class Meta:
        model = OrderDeliveryAttachment
        fields = [
            "id",
            "order",         # write-only (Order.id)
            "order_number",  # read-only (ORD_00001)
            "attachment_type",
            "file",
            "uploaded_at",
        ]

    def create(self, validated_data):
        """
        When you POST:
          - order (id)
          - attachment_type ("MANUFACTURER"/"TESTING")
          - file

        We auto-get-or-create OrderDeliveryInfo for that order,
        then attach this file to it.
        """
        order = validated_data.pop("order")
        delivery_info, _ = OrderDeliveryInfo.objects.get_or_create(order=order)
        return OrderDeliveryAttachment.objects.create(
            delivery_info=delivery_info, **validated_data
        )


# -------------------------------------------------------------------
# 3) DELIVERY INFO SERIALIZER (SCALAR FIELDS + READ-ONLY ATTACHMENT LISTS)
# -------------------------------------------------------------------

class OrderDeliveryInfoSerializer(serializers.ModelSerializer):
    """
    Per-order delivery info:
      - uin_registration_number
      - ready_for_delivery
      - manufacturer_attachments[] (read-only list)
      - testing_attachments[]      (read-only list)

    Attachments themselves are created via /api/order-delivery-attachments/
    using OrderDeliveryAttachmentSerializer.
    """

    # Show human-friendly order number
    order_number = serializers.CharField(
        source="order.order_number",
        read_only=True,
    )

    # Two read-only groups of attachments
    manufacturer_attachments = serializers.SerializerMethodField()
    testing_attachments = serializers.SerializerMethodField()

    class Meta:
        model = OrderDeliveryInfo
        fields = [
            "order",                  # PK = Order.id (read-only in practice)
            "order_number",
            "uin_registration_number",
            "ready_for_delivery",
            "manufacturer_attachments",
            "testing_attachments",
        ]
        # order is primary key; do not allow changing via API
        read_only_fields = ["order"]

    def get_manufacturer_attachments(self, obj):
        qs = obj.attachments.filter(attachment_type="MANUFACTURER")
        return OrderDeliveryAttachmentSerializer(
            qs, many=True, context=self.context
        ).data

    def get_testing_attachments(self, obj):
        qs = obj.attachments.filter(attachment_type="TESTING")
        return OrderDeliveryAttachmentSerializer(
            qs, many=True, context=self.context
        ).data


# -------------------------------------------------------------------
# 4) ORDER SERIALIZER (INCLUDES DELIVERY INFO)
# -------------------------------------------------------------------

class OrderSerializer(serializers.ModelSerializer):
    # Editable per-order checklist
    items = OrderItemSerializer(many=True, required=False)

    # Nested read-only delivery info block
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
            "items",
            "delivery_info",
        ]
        read_only_fields = ["order_number", "created_at", "updated_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", None)
        order = Order.objects.create(**validated_data)

        if items_data:
            for item_data in items_data:
                OrderItem.objects.create(order=order, **item_data)
        else:
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
        items_data = validated_data.pop("items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)

        return instance