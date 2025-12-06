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

    # allow any JSON type (string / list / dict / null)
    attachment = serializers.JSONField(
        required=False, allow_null=True
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
    # Helper: normalize client[].attachment (optional)
    # --------------------------------------------------
    def _normalize_client_attachments(self, uin_number, client_entries):
        """
        Clean up whatever frontend sends for client[].attachment
        into a string path, if present.

        Does NOT copy from top-level attachment. That is done in
        _fill_client_attachments_from_top().
        """
        if not client_entries:
            return client_entries or []

        normalized = []
        for entry in client_entries:
            entry = dict(entry)  # make a copy
            att = entry.get("attachment", None)

            # Treat empty dict/list as no attachment
            if isinstance(att, dict) and not att:
                att = None
            if isinstance(att, list) and not att:
                att = None

            if att is not None:
                # If it is a list, take first element
                if isinstance(att, list):
                    att = att[0] if att else ""

                # If it's a dict, try keys like 'name' or 'filename'
                if isinstance(att, dict):
                    if "name" in att:
                        att = att["name"]
                    elif "filename" in att:
                        att = att["filename"]
                    else:
                        att = str(att)

                # Convert non-string to string
                if not isinstance(att, str):
                    att = str(att)

                # If we also know the UIN, and att is only a filename,
                # we can prefix with folder. (optional – keep if you like)
                if uin_number and att and "/" not in att and "\\" not in att:
                    entry["attachment"] = f"drone_attachments/{uin_number}/{att}"
                else:
                    entry["attachment"] = att
            else:
                entry["attachment"] = None

            normalized.append(entry)

        return normalized

    # --------------------------------------------------
    # Helper: copy top-level attachment path into client[]
    # --------------------------------------------------
    def _fill_client_attachments_from_top(self, instance, client_entries):
        """
        If the top-level FileField 'attachment' is present, and a client entry
        has attachment empty / null / {} / [], copy the FileField path into it.

        Result: you get
          attachment: "http://127.0.0.1:8000/media/drone_attachments/..."
          client[i].attachment: "drone_attachments/.../file.png"
        """
        if not client_entries:
            return client_entries or []

        # No top-level file? nothing to copy
        if not instance.attachment or not hasattr(instance.attachment, "name"):
            return client_entries

        top_path = instance.attachment.name  # e.g. "drone_attachments/UIN/file.png"

        updated = []
        for entry in client_entries:
            entry = dict(entry)
            att = entry.get("attachment", None)

            if att in (None, "", {}, []):
                # copy direct relative path from FileField
                entry["attachment"] = top_path

            updated.append(entry)

        return updated

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------
    def validate_drone_id(self, value):
        if not value:
            return value
        qs = DroneRegistration.objects.filter(drone_id=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("drone_id must be unique.")
        return value

    # --------------------------------------------------
    # Create
    # --------------------------------------------------
    def create(self, validated_data):
        # Take out client_details from validated_data first
        client_entries = validated_data.pop("client_details", [])

        # First create instance so FileField is saved properly
        instance = super().create(validated_data)

        # Now we know UIN and attachment path
        uin_number = instance.uin_number

        # 1) Normalize any client attachments frontend sent
        client_entries = self._normalize_client_attachments(uin_number, client_entries)

        # 2) For entries with no attachment, copy from top-level FileField
        client_entries = self._fill_client_attachments_from_top(instance, client_entries)

        if client_entries:
            instance.client_details = client_entries
            instance.save(update_fields=["client_details"])

        return instance

    # --------------------------------------------------
    # Update
    # --------------------------------------------------
    def update(self, instance, validated_data):
        # Pull out client_details if present
        client_entries = validated_data.pop("client_details", None)

        # Update base fields (including top-level attachment) first
        instance = super().update(instance, validated_data)

        # Only touch client_details if it was provided in the request
        if client_entries is not None:
            uin_number = instance.uin_number

            # 1) Normalize what frontend sent
            client_entries = self._normalize_client_attachments(uin_number, client_entries)

            # 2) Copy top-level attachment path into empty client attachments
            client_entries = self._fill_client_attachments_from_top(instance, client_entries)

            instance.client_details = client_entries
            instance.save(update_fields=["client_details"])

        return instance

    # --------------------------------------------------
    # Read / Output
    # --------------------------------------------------
    def to_representation(self, instance):
        data = super().to_representation(instance)
        parent_drone_type = data.get("drone_type")

        client_entries = data.get("client") or []
        enriched_clients = []

        for entry in client_entries:
            entry = dict(entry)
            entry.setdefault("drone_type", parent_drone_type)
            enriched_clients.append(entry)

        data["client"] = enriched_clients
        return data
