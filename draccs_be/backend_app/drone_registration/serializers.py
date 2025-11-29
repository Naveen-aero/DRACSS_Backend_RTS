from rest_framework import serializers
from .models import DroneRegistration


#  One client entry inside the client list
class ClientEntrySerializer(serializers.Serializer):
    model_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    uin_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    drone_serial_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    flight_controller_serial_number = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    remote_controller = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    battery_charger_serial_number = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    battery_serial_number_1 = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    battery_serial_number_2 = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    # ❌ IMPORTANT: we do NOT declare drone_type / attachment here.
    # Those will be added only in the response via to_representation().


class DroneRegistrationSerializer(serializers.ModelSerializer):
    # Expose model.client_details as `client` in the API
    client = ClientEntrySerializer(
        many=True,
        source="client_details",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = DroneRegistration
        fields = [
            "id",
            "model_name",
            "drone_type",
            "manufacturer",
            "uin_number",
            "drone_serial_number",
            "drone_id",
            "flight_controller_serial_number",
            "remote_controller",
            "battery_charger_serial_number",
            "battery_serial_number_1",
            "battery_serial_number_2",
            "attachment",   # real FileField – this is where the file is stored
            "image",
            "registered",
            "is_active",
            "created_at",
            "updated_at",
            "client",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_drone_id(self, value):
        # Allow blank/None; if provided, enforce uniqueness manually to support partial updates.
        if not value:
            return value
        qs = DroneRegistration.objects.filter(drone_id=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("drone_id must be unique.")
        return value

    def to_representation(self, instance):
        """
        Keep existing behaviour for create/update, but when returning data:
        add `drone_type` and `attachment` to each `client` entry.
        """
        data = super().to_representation(instance)

        parent_drone_type = data.get("drone_type")
        parent_attachment = data.get("attachment")  # file URL or None

        client_entries = data.get("client") or []
        enriched_clients = []

        for entry in client_entries:
            # copy to avoid mutating internal state
            entry = dict(entry)

            # Only set if missing; do not overwrite if already present in JSON
            entry.setdefault("drone_type", parent_drone_type)
            entry.setdefault("attachment", parent_attachment)

            enriched_clients.append(entry)

        data["client"] = enriched_clients
        return data
