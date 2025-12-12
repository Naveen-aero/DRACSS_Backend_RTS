# from rest_framework import serializers
# from .models import DroneRegistration

    
# # One client entry inside the client list
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

#     # allow any JSON type (string / list / dict / null)
#     attachment = serializers.JSONField(
#         required=False, allow_null=True
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
#             "attachment",   # top-level FileField
#             "image",
#             "registered",
#             "is_active",
#             "created_at",
#             "updated_at",
#             "client",
#         ]
#         read_only_fields = ["id", "created_at", "updated_at"]

#     # --------------------------------------------------
#     # Helper: normalize client[].attachment paths (for DB)
#     # --------------------------------------------------
#     def _normalize_client_attachments(self, uin_number, client_entries):
#         """
#         Ensure each client entry's 'attachment' is stored under:
#             drone_attachments/<uin_number>/<filename>
#         if only a bare filename is provided.
#         Accepts attachment as string, list, dict, etc.
#         """
#         if not client_entries:
#             return client_entries or []

#         # If there is no UIN, just return as-is (nothing to prefix with)
#         if not uin_number:
#             return [dict(entry) for entry in client_entries]

#         normalized = []
#         for entry in client_entries:
#             entry = dict(entry)  # make a copy to avoid mutating in-place
#             att = entry.get("attachment")

#             # Treat empty dict/list as no attachment
#             if isinstance(att, dict) and not att:
#                 att = None
#             if isinstance(att, list) and not att:
#                 att = None

#             if att is not None:
#                 # If it is a list, take first element
#                 if isinstance(att, list):
#                     att = att[0] if att else ""

#                 # If it's a dict, try common keys like 'name' or 'filename'
#                 if isinstance(att, dict):
#                     if "name" in att:
#                         att = att["name"]
#                     elif "filename" in att:
#                         att = att["filename"]
#                     else:
#                         att = str(att)

#                 # If it's some other type (file object / int / etc), cast to string
#                 if not isinstance(att, str):
#                     att = str(att)

#                 if att:
#                     # If already a URL, keep it
#                     if att.startswith("http://") or att.startswith("https://"):
#                         entry["attachment"] = att
#                     # If no slash in value, treat it as a simple filename
#                     elif "/" not in att and "\\" not in att:
#                         entry["attachment"] = f"drone_attachments/{uin_number}/{att}"
#                     else:
#                         entry["attachment"] = att  # already a path
#                 else:
#                     entry["attachment"] = None
#             else:
#                 entry["attachment"] = None

#             normalized.append(entry)

#         return normalized

#     # --------------------------------------------------
#     # Validation
#     # --------------------------------------------------
#     def validate_drone_id(self, value):
#         if not value:
#             return value
#         qs = DroneRegistration.objects.filter(drone_id=value)
#         if self.instance:
#             qs = qs.exclude(pk=self.instance.pk)
#         if qs.exists():
#             raise serializers.ValidationError("drone_id must be unique.")
#         return value

#     # --------------------------------------------------
#     # Create / Update (write side)
#     # --------------------------------------------------
#     def create(self, validated_data):
#         client_entries = validated_data.pop("client_details", [])
#         uin_number = validated_data.get("uin_number")

#         client_entries = self._normalize_client_attachments(uin_number, client_entries)
#         validated_data["client_details"] = client_entries

#         instance = super().create(validated_data)
#         return instance

#     def update(self, instance, validated_data):
#         """
#         On update:
#         - If client_details is provided and some entries have no attachment,
#           we can still normalize any attachments that are provided.
#         """
#         if "client_details" in validated_data:
#             client_entries = validated_data.get("client_details") or []
#             uin_number = validated_data.get("uin_number", instance.uin_number)
#             client_entries = self._normalize_client_attachments(uin_number, client_entries)
#             validated_data["client_details"] = client_entries

#         return super().update(instance, validated_data)

#     # --------------------------------------------------
#     # Read / Output
#     # --------------------------------------------------
#     def to_representation(self, instance):
#         """
#         When returning data:
#         - client_details already contains normalized attachment paths
#         - Only auto-fill drone_type from parent if missing
#         -  Mirror top-level attachment URL into each client[].attachment
#           if top-level attachment exists.
#         """
#         data = super().to_representation(instance)

#         parent_drone_type = data.get("drone_type")
#         top_attachment = data.get("attachment")  # e.g. full URL from FileField

#         client_entries = data.get("client") or []
#         enriched_clients = []

#         for entry in client_entries:
#             entry = dict(entry)

#             # Only set drone_type if missing; do not overwrite if already present
#             entry.setdefault("drone_type", parent_drone_type)

#             #  key line: if we have a top-level attachment URL, reuse it for the client
#             if top_attachment:
#                 entry["attachment"] = top_attachment

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
    attachment = serializers.JSONField(required=False, allow_null=True)


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
            "remarks",
            "is_active",
            "created_at",
            "updated_at",
            "client",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    # --------------------------------------------------
    # Helper: normalize client[].attachment paths (for DB)
    # --------------------------------------------------
    def _normalize_client_attachments(self, uin_number, client_entries):
        """
        Ensure each client entry's 'attachment' is stored under:
            drone_attachments/<uin_number>/<filename>
        if only a bare filename is provided.
        Accepts attachment as string, list, dict, etc.
        """
        if not client_entries:
            return client_entries or []

        if not uin_number:
            return [dict(entry) for entry in client_entries]

        normalized = []
        for entry in client_entries:
            entry = dict(entry)
            att = entry.get("attachment")

            if isinstance(att, dict) and not att:
                att = None
            if isinstance(att, list) and not att:
                att = None

            if att is not None:
                if isinstance(att, list):
                    att = att[0] if att else ""

                if isinstance(att, dict):
                    if "name" in att:
                        att = att["name"]
                    elif "filename" in att:
                        att = att["filename"]
                    else:
                        att = str(att)

                if not isinstance(att, str):
                    att = str(att)

                if att:
                    if att.startswith("http://") or att.startswith("https://"):
                        entry["attachment"] = att
                    elif "/" not in att and "\\" not in att:
                        entry["attachment"] = f"drone_attachments/{uin_number}/{att}"
                    else:
                        entry["attachment"] = att
                else:
                    entry["attachment"] = None
            else:
                entry["attachment"] = None

            normalized.append(entry)

        return normalized

    # --------------------------------------------------
    # Validation for drone_id uniqueness
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
    #  Global validation rules (CREATE + UPDATE)
    # --------------------------------------------------
    def validate(self, attrs):
        is_create = self.instance is None

        # Fallback to instance values for PATCH
        is_active = attrs.get("is_active", getattr(self.instance, "is_active", None))
        remarks = attrs.get("remarks", getattr(self.instance, "remarks", None))

        #  CREATE rules:
        # - DO NOT validate/deny "registered" here
        #   because Browsable API HTML form may send it automatically.
        # - is_active must start NULL
        if is_create:
            if "is_active" in attrs and attrs.get("is_active") is not None:
                raise serializers.ValidationError({
                    "is_active": "On creation, 'is_active' must be null/empty. Update later to true/false."
                })

            # Optional: keep remarks empty on create
            if "remarks" in attrs and str(attrs.get("remarks") or "").strip() != "":
                raise serializers.ValidationError({
                    "remarks": "On creation, keep 'remarks' empty. Remarks is required only when is_active is set to false."
                })

        # remarks required ONLY when is_active == False
        if is_active is False:
            if remarks is None or str(remarks).strip() == "":
                raise serializers.ValidationError({
                    "remarks": "Remarks is required when 'is_active' is false."
                })

        return attrs

    # --------------------------------------------------
    # Create / Update (write side)
    # --------------------------------------------------
    def create(self, validated_data):
        #  IMPORTANT: Browsable API may send registered;
        # ignore it and force False always on create
        validated_data.pop("registered", None)

        client_entries = validated_data.pop("client_details", [])
        uin_number = validated_data.get("uin_number")

        client_entries = self._normalize_client_attachments(uin_number, client_entries)
        validated_data["client_details"] = client_entries

        #  FORCE registered = False on CREATE
        validated_data["registered"] = False

        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        """
        On update:
        - If client_details provided: normalize attachments.
        - Optional: clear remarks automatically when is_active becomes True and user didn't send remarks.
        """
        # Optional: if user sets is_active True and doesn't send remarks, clear it
        if "remarks" not in validated_data:
            new_is_active = validated_data.get("is_active", instance.is_active)
            if new_is_active is True:
                validated_data["remarks"] = None

        if "client_details" in validated_data:
            client_entries = validated_data.get("client_details") or []
            uin_number = validated_data.get("uin_number", instance.uin_number)
            client_entries = self._normalize_client_attachments(uin_number, client_entries)
            validated_data["client_details"] = client_entries

        return super().update(instance, validated_data)

    # --------------------------------------------------
    # Read / Output
    # --------------------------------------------------
    def to_representation(self, instance):
        data = super().to_representation(instance)

        parent_drone_type = data.get("drone_type")
        top_attachment = data.get("attachment")

        client_entries = data.get("client") or []
        enriched_clients = []

        for entry in client_entries:
            entry = dict(entry)
            entry.setdefault("drone_type", parent_drone_type)

            if top_attachment:
                entry["attachment"] = top_attachment

            enriched_clients.append(entry)

        data["client"] = enriched_clients
        return data
