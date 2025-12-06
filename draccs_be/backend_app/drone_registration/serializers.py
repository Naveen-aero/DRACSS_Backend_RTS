# from rest_framework import serializers
# from .models import DroneRegistration


# #  One client entry inside the client list
# class ClientEntrySerializer(serializers.Serializer):
#     model_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
#     drone_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
#     uin_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
#     drone_serial_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
#     flight_controller_serial_number = serializers.CharField(
#         required=False, allow_blank=True, allow_null=True
#     )
#     remote_controller = serializers.CharField(
#         required=False, allow_blank=True, allow_null=True
#     )
#     battery_charger_serial_number = serializers.CharField(
#         required=False, allow_blank=True, allow_null=True
#     )
#     battery_serial_number_1 = serializers.CharField(
#         required=False, allow_blank=True, allow_null=True
#     )
#     battery_serial_number_2 = serializers.CharField(
#         required=False, allow_blank=True, allow_null=True
#     )

#     #  NEW: per-client attachment (string/URL/path stored in JSON)
#     attachment = serializers.CharField(
#         required=False, allow_blank=True, allow_null=True
#     )


# class DroneRegistrationSerializer(serializers.ModelSerializer):
#     # Expose model.client_details as `client` in the API
#     client = ClientEntrySerializer(
#         many=True,
#         source="client_details",
#         required=False,
#         allow_null=True,
#     )

#     class Meta:
#         model = DroneRegistration
#         fields = [
#             "id",
#             "model_name",
#             "drone_type",
#             "manufacturer",
#             "uin_number",
#             "drone_serial_number",
#             "drone_id",
#             "flight_controller_serial_number",
#             "remote_controller",
#             "battery_charger_serial_number",
#             "battery_serial_number_1",
#             "battery_serial_number_2",
#             "attachment",   # real FileField – stored on model
#             "image",
#             "registered",
#             "is_active",
#             "created_at",
#             "updated_at",
#             "client",
#         ]
#         read_only_fields = ["id", "created_at", "updated_at"]

#     def validate_drone_id(self, value):
#         # Allow blank/None; if provided, enforce uniqueness manually to support partial updates.
#         if not value:
#             return value
#         qs = DroneRegistration.objects.filter(drone_id=value)
#         if self.instance:
#             qs = qs.exclude(pk=self.instance.pk)
#         if qs.exists():
#             raise serializers.ValidationError("drone_id must be unique.")
#         return value

#     def to_representation(self, instance):
#         """
#         When returning data:
#         - Keep client_details as-is for attachment
#         - Only auto-fill drone_type from parent if missing
#         """
#         data = super().to_representation(instance)

#         parent_drone_type = data.get("drone_type")

#         client_entries = data.get("client") or []
#         enriched_clients = []

#         for entry in client_entries:
#             entry = dict(entry)

#             # Only set drone_type if missing; do not overwrite if already present in JSON
#             entry.setdefault("drone_type", parent_drone_type)

#             # Do NOT touch entry['attachment'] here
#             # It will be whatever was stored in client_details.

#             enriched_clients.append(entry)

#         data["client"] = enriched_clients
#         return data


from rest_framework import serializers
from .models import DroneRegistration


# One client entry inside the client list
class ClientEntrySerializer(serializers.Serializer):
    model_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    drone_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
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

    #  This is the client-specific attachment (URL/path as string)
    attachment = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )


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
            "attachment",   # top-level FileField
            "image",
            "registered",
            "is_active",
            "created_at",
            "updated_at",
            "client",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    # --------------------------------------------------
    # Helper: normalize client[].attachment paths
    # --------------------------------------------------
    def _normalize_client_attachments(self, uin_number, client_entries):
        """
        Ensure each client entry's 'attachment' is stored under:
            drone_attachments/<uin_number>/<filename>
        if only a bare filename is provided.

        Example:
            uin_number = "1234567"
            attachment = "invoice1.pdf"
        becomes:
            "drone_attachments/1234567/invoice1.pdf"
        """
        if not client_entries:
            return client_entries or []

        # If there is no UIN, just return as-is (nothing to prefix with)
        if not uin_number:
            return [dict(entry) for entry in client_entries]

        normalized = []
        for entry in client_entries:
            entry = dict(entry)  # make a copy to avoid mutating in-place
            att = entry.get("attachment")

            if att:
                # If no slash in value, treat it as a simple filename
                if "/" not in att and "\\" not in att:
                    entry["attachment"] = f"drone_attachments/{uin_number}/{att}"
                # else: assume frontend already sent a full/relative path – leave it

            normalized.append(entry)

        return normalized

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Create / Update (write side)
    # --------------------------------------------------
    def create(self, validated_data):
        # client_details comes from "client" via source="client_details"
        client_entries = validated_data.pop("client_details", [])

        # Need UIN to build folder path for attachments inside client[]
        uin_number = validated_data.get("uin_number")

        client_entries = self._normalize_client_attachments(uin_number, client_entries)
        validated_data["client_details"] = client_entries

        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        # Only normalize client_details if they are part of the incoming update
        if "client_details" in validated_data:
            client_entries = validated_data.get("client_details") or []
            # Use new UIN if provided, otherwise existing one on instance
            uin_number = validated_data.get("uin_number", instance.uin_number)
            client_entries = self._normalize_client_attachments(uin_number, client_entries)
            validated_data["client_details"] = client_entries

        return super().update(instance, validated_data)

    # --------------------------------------------------
    # Read / Output
    # --------------------------------------------------
    def to_representation(self, instance):
        """
        When returning data:
        - client_details already contains normalized attachment paths
        - Only auto-fill drone_type from parent if missing
        """
        data = super().to_representation(instance)

        parent_drone_type = data.get("drone_type")

        client_entries = data.get("client") or []
        enriched_clients = []

        for entry in client_entries:
            entry = dict(entry)

            # Only set drone_type if missing; do not overwrite if already present
            entry.setdefault("drone_type", parent_drone_type)

            # attachment is already a path string; just pass through
            enriched_clients.append(entry)

        data["client"] = enriched_clients
        return data
