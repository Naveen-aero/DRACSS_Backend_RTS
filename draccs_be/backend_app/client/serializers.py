from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    
    drones = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    class Meta:
        model = Client
        fields = [
            "client_id",
            "name",
            "phone",
            "email",
            "location",
            "id_proof",
            "bank_name",
            "account_number",
            "ifsc_code",
            "branch_name",
            "created_at",
            "drones",
        ]
        read_only_fields = ["client_id", "created_at"]

    def update(self, instance, validated_data):
        """
        Custom update to APPEND to drones list instead of replacing it.
        """
        # Take drones from incoming data if present
        new_drones = validated_data.pop("drones", None)

        if new_drones is not None:
            # Existing stored list
            existing = instance.drones or []

            # Append new values, avoid duplicates (optional)
            merged = existing + [d for d in new_drones if d not in existing]

            instance.drones = merged
            instance.save(update_fields=["drones"])

        # Update other normal fields
        return super().update(instance, validated_data)
