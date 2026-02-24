from rest_framework import serializers
from .models import ReturnToBaseServiceRequest, RTBServiceRequestComponent


class RTBServiceRequestComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RTBServiceRequestComponent
        fields = ["id", "component_type", "quantity", "remarks", "price", "gst", "total"]
        read_only_fields = ["id", "total"]

    def validate_quantity(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate_price(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate_gst(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("GST cannot be negative.")
        if value is not None and value > 100:
            raise serializers.ValidationError("GST cannot be greater than 100%.")
        return value


class ReturnToBaseServiceRequestSerializer(serializers.ModelSerializer):
    components = RTBServiceRequestComponentSerializer(many=True, required=False)

    class Meta:
        model = ReturnToBaseServiceRequest
        fields = "__all__"

    def validate(self, attrs):
        total_hours = attrs.get("total_accumulated_hours")
        if total_hours is not None and total_hours < 0:
            raise serializers.ValidationError(
                {"total_accumulated_hours": "Total accumulated hours cannot be negative."}
            )

        occ = attrs.get("date_of_occurrence")
        rep = attrs.get("reported_date")
        if occ and rep and rep < occ:
            raise serializers.ValidationError(
                {"reported_date": "Reported date cannot be earlier than date of occurrence."}
            )

        in_ship = attrs.get("intrack_shipping_date")
        in_exp = attrs.get("intrack_expected_date")
        if in_ship and in_exp and in_exp < in_ship:
            raise serializers.ValidationError(
                {"intrack_expected_date": "Intrack expected date cannot be earlier than intrack shipping date."}
            )

        in_tid = attrs.get("intrack_tracking_id")
        in_courier = attrs.get("intrack_courier")
        if in_tid and not in_courier:
            raise serializers.ValidationError(
                {"intrack_courier": "Intrack courier is required when intrack tracking id is provided."}
            )

        out_ship = attrs.get("outtrack_shipping_date")
        out_exp = attrs.get("outtrack_expected_date")
        if out_ship and out_exp and out_exp < out_ship:
            raise serializers.ValidationError(
                {"outtrack_expected_date": "Outtrack expected date cannot be earlier than outtrack shipping date."}
            )

        out_tid = attrs.get("outtrack_tracking_id")
        out_courier = attrs.get("outtrack_courier")
        if out_tid and not out_courier:
            raise serializers.ValidationError(
                {"outtrack_courier": "Outtrack courier is required when outtrack tracking id is provided."}
            )

        return attrs

    def create(self, validated_data):
        components_data = validated_data.pop("components", [])
        rtb = ReturnToBaseServiceRequest.objects.create(**validated_data)

        for item in components_data:
            RTBServiceRequestComponent.objects.create(rtb_request=rtb, **item)

        return rtb

    def update(self, instance, validated_data):
        components_data = validated_data.pop("components", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if components_data is not None:
            existing_map = {c.id: c for c in instance.components.all()}

            for item in components_data:
                comp_id = item.get("id")

                if comp_id and comp_id in existing_map:
                    comp = existing_map[comp_id]

                    for field in ["component_type", "quantity", "remarks", "price", "gst"]:
                        if field in item:
                            setattr(comp, field, item[field])

                    comp.save()
                else:
                    RTBServiceRequestComponent.objects.create(
                        rtb_request=instance,
                        **{k: v for k, v in item.items() if k != "id"}
                    )

        return instance