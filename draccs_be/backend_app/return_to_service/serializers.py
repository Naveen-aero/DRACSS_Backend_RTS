from rest_framework import serializers
from .models import ReturnToBaseServiceRequest, RTBServiceRequestComponent


class RTBServiceRequestComponentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = RTBServiceRequestComponent
        fields = ["id", "component_type", "quantity", "remarks"]


class ReturnToBaseServiceRequestSerializer(serializers.ModelSerializer):
    #  NEW: nested components inside SAME endpoint
    components = RTBServiceRequestComponentSerializer(many=True, required=False)

    class Meta:
        model = ReturnToBaseServiceRequest
        fields = "__all__"

    def validate(self, attrs):
        # -----------------------------
        # Existing validations
        # -----------------------------
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

        # -----------------------------
        # NEW: INTRACK validations
        # -----------------------------
        in_ship = attrs.get("intrack_shipping_date")
        in_exp = attrs.get("intrack_expected_date")
        if in_ship and in_exp and in_exp < in_ship:
            raise serializers.ValidationError(
                {"intrack_expected_date": "Intrack expected date cannot be earlier than intrack shipping date."}
            )

        # (Optional) if tracking id is given, courier should be present
        in_tid = attrs.get("intrack_tracking_id")
        in_courier = attrs.get("intrack_courier")
        if in_tid and not in_courier:
            raise serializers.ValidationError(
                {"intrack_courier": "Intrack courier is required when intrack tracking id is provided."}
            )

        # -----------------------------
        #  NEW: OUTTRACK validations
        # -----------------------------
        out_ship = attrs.get("outtrack_shipping_date")
        out_exp = attrs.get("outtrack_expected_date")
        if out_ship and out_exp and out_exp < out_ship:
            raise serializers.ValidationError(
                {"outtrack_expected_date": "Outtrack expected date cannot be earlier than outtrack shipping date."}
            )

        # (Optional) if tracking id is given, courier should be present
        out_tid = attrs.get("outtrack_tracking_id")
        out_courier = attrs.get("outtrack_courier")
        if out_tid and not out_courier:
            raise serializers.ValidationError(
                {"outtrack_courier": "Outtrack courier is required when outtrack tracking id is provided."}
            )

        return attrs

    #  NEW: supports POST with components[]
    def create(self, validated_data):
        components_data = validated_data.pop("components", [])
        rtb = ReturnToBaseServiceRequest.objects.create(**validated_data)

        for item in components_data:
            RTBServiceRequestComponent.objects.create(rtb_request=rtb, **item)

        return rtb

    # NEW: supports PUT/PATCH with components[]
    # Rule:
    # - if components key is present -> replace all components
    # - if components key not present -> do nothing to components
    def update(self, instance, validated_data):
        components_data = validated_data.pop("components", None)

        # update parent normally (existing behavior)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # update components only if provided
        if components_data is not None:
            instance.components.all().delete()
            for item in components_data:
                RTBServiceRequestComponent.objects.create(rtb_request=instance, **item)

        return instance
