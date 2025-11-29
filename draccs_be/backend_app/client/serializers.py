from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
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
        ]
        read_only_fields = ["client_id", "created_at"]
