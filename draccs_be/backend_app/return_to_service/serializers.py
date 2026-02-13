from rest_framework import serializers
from .models import ReturnToBaseServiceRequest


class ReturnToBaseServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnToBaseServiceRequest
        fields = "__all__"

    def validate(self, attrs):
        # Basic safety checks (optional but production-friendly)
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

        return attrs