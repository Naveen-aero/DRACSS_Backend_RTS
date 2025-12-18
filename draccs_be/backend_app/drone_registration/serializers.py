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
#     attachment = serializers.JSONField(required=False, allow_null=True)


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
#             "remarks",
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

#         if not uin_number:
#             return [dict(entry) for entry in client_entries]

#         normalized = []
#         for entry in client_entries:
#             entry = dict(entry)
#             att = entry.get("attachment")

#             if isinstance(att, dict) and not att:
#                 att = None
#             if isinstance(att, list) and not att:
#                 att = None

#             if att is not None:
#                 if isinstance(att, list):
#                     att = att[0] if att else ""

#                 if isinstance(att, dict):
#                     if "name" in att:
#                         att = att["name"]
#                     elif "filename" in att:
#                         att = att["filename"]
#                     else:
#                         att = str(att)

#                 if not isinstance(att, str):
#                     att = str(att)

#                 if att:
#                     if att.startswith("http://") or att.startswith("https://"):
#                         entry["attachment"] = att
#                     elif "/" not in att and "\\" not in att:
#                         entry["attachment"] = f"drone_attachments/{uin_number}/{att}"
#                     else:
#                         entry["attachment"] = att
#                 else:
#                     entry["attachment"] = None
#             else:
#                 entry["attachment"] = None

#             normalized.append(entry)

#         return normalized

#     # --------------------------------------------------
#     # Validation for drone_id uniqueness
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
#     #  Global validation rules (CREATE + UPDATE)
#     # --------------------------------------------------
#     def validate(self, attrs):
#         is_create = self.instance is None

#         # Fallback to instance values for PATCH
#         is_active = attrs.get("is_active", getattr(self.instance, "is_active", None))
#         remarks = attrs.get("remarks", getattr(self.instance, "remarks", None))

#         #  CREATE rules:
#         # - DO NOT validate/deny "registered" here
#         #   because Browsable API HTML form may send it automatically.
#         # - is_active must start NULL
#         if is_create:
#             if "is_active" in attrs and attrs.get("is_active") is not None:
#                 raise serializers.ValidationError({
#                     "is_active": "On creation, 'is_active' must be null/empty. Update later to true/false."
#                 })

#             # Optional: keep remarks empty on create
#             if "remarks" in attrs and str(attrs.get("remarks") or "").strip() != "":
#                 raise serializers.ValidationError({
#                     "remarks": "On creation, keep 'remarks' empty. Remarks is required only when is_active is set to false."
#                 })

#         # remarks required ONLY when is_active == False
#         if is_active is False:
#             if remarks is None or str(remarks).strip() == "":
#                 raise serializers.ValidationError({
#                     "remarks": "Remarks is required when 'is_active' is false."
#                 })

#         return attrs

#     # --------------------------------------------------
#     # Create / Update (write side)
#     # --------------------------------------------------
#     def create(self, validated_data):
#         #  IMPORTANT: Browsable API may send registered;
#         # ignore it and force False always on create
#         validated_data.pop("registered", None)

#         client_entries = validated_data.pop("client_details", [])
#         uin_number = validated_data.get("uin_number")

#         client_entries = self._normalize_client_attachments(uin_number, client_entries)
#         validated_data["client_details"] = client_entries

#         #  FORCE registered = False on CREATE
#         validated_data["registered"] = False

#         instance = super().create(validated_data)
#         return instance

#     def update(self, instance, validated_data):
#         """
#         On update:
#         - If client_details provided: normalize attachments.
#         - Optional: clear remarks automatically when is_active becomes True and user didn't send remarks.
#         """
#         # Optional: if user sets is_active True and doesn't send remarks, clear it
#         if "remarks" not in validated_data:
#             new_is_active = validated_data.get("is_active", instance.is_active)
#             if new_is_active is True:
#                 validated_data["remarks"] = None

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
#         data = super().to_representation(instance)

#         parent_drone_type = data.get("drone_type")
#         top_attachment = data.get("attachment")

#         client_entries = data.get("client") or []
#         enriched_clients = []

#         for entry in client_entries:
#             entry = dict(entry)
#             entry.setdefault("drone_type", parent_drone_type)

#             if top_attachment:
#                 entry["attachment"] = top_attachment

#             enriched_clients.append(entry)

#         data["client"] = enriched_clients
#         return data


# import json
# from django.conf import settings
# from django.core.files.storage import default_storage
# from django.utils.text import get_valid_filename
# from rest_framework import serializers
# from .models import DroneRegistration


# class ClientEntrySerializer(serializers.Serializer):
#     model_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
#     drone_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
#     uin_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
#     drone_serial_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
#     flight_controller_serial_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
#     remote_controller = serializers.CharField(required=False, allow_blank=True, allow_null=True)
#     battery_charger_serial_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
#     battery_serial_number_1 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
#     battery_serial_number_2 = serializers.CharField(required=False, allow_blank=True, allow_null=True)

#     # Accept string / {} / [] / null from frontend
#     attachment = serializers.JSONField(required=False, allow_null=True)

#     def validate_attachment(self, value):
#         # Normalize empty-ish values into None
#         if value in ({}, [], "", None):
#             return None

#         if isinstance(value, str):
#             v = value.strip()
#             return v if v else None

#         if isinstance(value, list):
#             if not value:
#                 return None
#             first = value[0]
#             if isinstance(first, str):
#                 first = first.strip()
#                 return first if first else None
#             return None

#         if isinstance(value, dict):
#             for k in ("url", "path", "name", "filename"):
#                 v = value.get(k)
#                 if isinstance(v, str):
#                     v = v.strip()
#                     return v if v else None
#             return None

#         return None


# class DroneRegistrationSerializer(serializers.ModelSerializer):
#     client = ClientEntrySerializer(many=True, source="client_details", required=False, allow_null=True)

#     class Meta:
#         model = DroneRegistration
#         fields = [
#             "id", "model_name", "drone_type", "manufacturer",
#             "uin_number", "drone_serial_number", "drone_id",
#             "flight_controller_serial_number", "remote_controller",
#             "battery_charger_serial_number", "battery_serial_number_1", "battery_serial_number_2",
#             "attachment", "image",
#             "registered", "remarks", "is_active",
#             "created_at", "updated_at",
#             "client",
#         ]
#         read_only_fields = ["id", "created_at", "updated_at"]

#     # -------------------------------------------------------
#     # IMPORTANT: parse multipart "client" JSON string -> list
#     # -------------------------------------------------------
#     def to_internal_value(self, data):
#         # When data is QueryDict (multipart/form-data), "client" arrives as string
#         client_val = data.get("client", None)
#         if isinstance(client_val, str):
#             try:
#                 parsed = json.loads(client_val)
#                 data = data.copy()
#                 data["client"] = parsed
#             except Exception:
#                 pass
#         return super().to_internal_value(data)

#     # -------------------------------------------------------
#     # Save client attachment files from multipart request.FILES
#     # -------------------------------------------------------
#     def _save_client_attachment_files(self, parent_uin, client_entries):
#         """
#         Accept nested uploads:
#           client_0_attachment, client_1_attachment, ...
#         Save to: drone_attachments/<uin>/<filename>
#         Store RELATIVE PATH in JSON (ex: drone_attachments/123/buzzer.jpg)

#         NOTE: Uses client entry uin_number if available, else parent_uin.
#         """
#         request = self.context.get("request")
#         if not request or not hasattr(request, "FILES"):
#             return client_entries or []

#         client_entries = client_entries or []
#         updated = []

#         for idx, entry in enumerate(client_entries):
#             entry = dict(entry or {})

#             uin = entry.get("uin_number") or parent_uin
#             if not uin:
#                 updated.append(entry)
#                 continue

#             f = request.FILES.get(f"client_{idx}_attachment")
#             if f:
#                 filename = get_valid_filename(f.name)
#                 save_path = f"drone_attachments/{uin}/{filename}"
#                 saved_path = default_storage.save(save_path, f)
#                 entry["attachment"] = saved_path  # store relative path

#             updated.append(entry)

#         return updated

#     # -------------------------------------------------------
#     # Create / Update
#     # -------------------------------------------------------
#     def create(self, validated_data):
#         validated_data.pop("registered", None)

#         client_entries = validated_data.pop("client_details", []) or []
#         parent_uin = validated_data.get("uin_number")

#         client_entries = self._save_client_attachment_files(parent_uin, client_entries)
#         validated_data["client_details"] = client_entries

#         validated_data["registered"] = False
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         if "client_details" in validated_data:
#             client_entries = validated_data.get("client_details") or []
#             parent_uin = validated_data.get("uin_number", instance.uin_number)

#             client_entries = self._save_client_attachment_files(parent_uin, client_entries)
#             validated_data["client_details"] = client_entries

#         return super().update(instance, validated_data)

#     # -------------------------------------------------------
#     # Read: convert relative client attachment -> full URL
#     # -------------------------------------------------------
#     def to_representation(self, instance):
#         data = super().to_representation(instance)

#         parent_drone_type = data.get("drone_type")
#         request = self.context.get("request")
#         media_url = getattr(settings, "MEDIA_URL", "/media/")

#         client_entries = data.get("client") or []
#         enriched = []

#         for entry in client_entries:
#             entry = dict(entry or {})

#             if not entry.get("drone_type"):
#                 entry["drone_type"] = parent_drone_type

#             att = entry.get("attachment")
#             if att and isinstance(att, str) and not att.startswith("http"):
#                 rel = att.lstrip("/")
#                 url = f"{media_url.rstrip('/')}/{rel}"
#                 entry["attachment"] = request.build_absolute_uri(url) if request else url

#             # DO NOT fallback from parent attachment (keep separate)
#             enriched.append(entry)

#         data["client"] = enriched
#         return data

# serializers.py
import json
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.text import get_valid_filename
from rest_framework import serializers
from .models import DroneRegistration


class ClientEntrySerializer(serializers.Serializer):
    # Canonical keys stored inside JSONField
    model_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    drone_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    uin_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    drone_serial_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    flight_controller_serial_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    remote_controller = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    battery_charger_serial_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    battery_serial_number_1 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    battery_serial_number_2 = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # store string path in JSON (recommended), but accept junk from frontend too
    attachment = serializers.JSONField(required=False, allow_null=True)

    def validate_attachment(self, value):
        # normalize empty-ish values into None
        if value in ({}, [], "", None):
            return None

        if isinstance(value, str):
            v = value.strip()
            return v if v else None

        if isinstance(value, list):
            if not value:
                return None
            first = value[0]
            if isinstance(first, str):
                first = first.strip()
                return first if first else None
            return None

        if isinstance(value, dict):
            for k in ("url", "path", "name", "filename"):
                v = value.get(k)
                if isinstance(v, str):
                    v = v.strip()
                    return v if v else None
            return None

        return None


class DroneRegistrationSerializer(serializers.ModelSerializer):
    # DB field is client_details (JSONField). API field is "client".
    client = ClientEntrySerializer(
        many=True, source="client_details", required=False, allow_null=True
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
            "attachment",
            "image",
            "registered",
            "remarks",
            "is_active",
            "created_at",
            "updated_at",
            "client",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    # -------------------------------------------------------
    # Parse client (multipart) + map c_* -> canonical keys
    # -------------------------------------------------------
    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, "copy") else dict(data)

        client_val = data.get("client", None)

        # multipart/form-data: client arrives as JSON string
        if isinstance(client_val, str):
            try:
                client_val = json.loads(client_val)
            except Exception:
                client_val = None

        # normalize dict -> list
        if isinstance(client_val, dict):
            client_val = [client_val]

        # Map c_* -> canonical for WRITE
        if isinstance(client_val, list):
            mapped = []
            for e in client_val:
                e = dict(e or {})
                mapped.append(
                    {
                        "model_name": e.get("model_name") or e.get("c_model_name"),
                        "drone_type": e.get("drone_type") or e.get("c_drone_type"),
                        "uin_number": e.get("uin_number") or e.get("c_uin_number"),
                        "drone_serial_number": e.get("drone_serial_number")
                        or e.get("c_drone_serial_number"),
                        "flight_controller_serial_number": e.get(
                            "flight_controller_serial_number"
                        )
                        or e.get("c_flight_controller_serial_number"),
                        "remote_controller": e.get("remote_controller")
                        or e.get("c_remote_controller"),
                        "battery_charger_serial_number": e.get(
                            "battery_charger_serial_number"
                        )
                        or e.get("c_battery_charger_serial_number"),
                        "battery_serial_number_1": e.get("battery_serial_number_1")
                        or e.get("c_battery_serial_number_1"),
                        "battery_serial_number_2": e.get("battery_serial_number_2")
                        or e.get("c_battery_serial_number_2"),
                        "attachment": e.get("attachment") or e.get("c_attachment"),
                    }
                )
            data["client"] = mapped

        return super().to_internal_value(data)

    # -------------------------------------------------------
    # Save nested client attachment files
    # -------------------------------------------------------
    def _save_client_attachment_files(self, parent_uin, client_entries):
        """
        Supports:
          - client_0_attachment, client_1_attachment, ... (recommended)
          - c_attachment (single quick upload for client[0])
        Saves under: drone_attachments/<uin>/<filename>
        Stores RELATIVE PATH in JSON: drone_attachments/<uin>/<file>
        """
        request = self.context.get("request")
        if not request or not hasattr(request, "FILES"):
            return client_entries or []

        client_entries = client_entries or []
        updated = []

        for idx, entry in enumerate(client_entries):
            entry = dict(entry or {})
            uin = entry.get("uin_number") or parent_uin

            # preferred per-index key
            f = request.FILES.get(f"client_{idx}_attachment")

            # fallback: single key for first client
            if not f and idx == 0:
                f = request.FILES.get("c_attachment")

            if f and uin:
                filename = get_valid_filename(f.name)
                save_path = f"drone_attachments/{uin}/{filename}"
                saved_path = default_storage.save(save_path, f)
                entry["attachment"] = saved_path  # relative path in JSON

            updated.append(entry)

        return updated

    # -------------------------------------------------------
    # Create / Update
    # -------------------------------------------------------
    def create(self, validated_data):
        validated_data.pop("registered", None)

        client_entries = validated_data.pop("client_details", []) or []
        parent_uin = validated_data.get("uin_number")

        client_entries = self._save_client_attachment_files(parent_uin, client_entries)
        validated_data["client_details"] = client_entries

        validated_data["registered"] = False
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get("request")

        # If file is sent but no client provided, DO NOT overwrite existing clients.
        # Instead: update the first client entry if it exists, else create one.
        if (
            "client_details" not in validated_data
            and request
            and hasattr(request, "FILES")
            and request.FILES.get("c_attachment")
        ):
            existing = instance.client_details or []
            if isinstance(existing, list) and len(existing) > 0:
                validated_data["client_details"] = existing
            else:
                validated_data["client_details"] = [{}]

        if "client_details" in validated_data:
            client_entries = validated_data.get("client_details") or []
            parent_uin = validated_data.get("uin_number", instance.uin_number)

            client_entries = self._save_client_attachment_files(parent_uin, client_entries)
            validated_data["client_details"] = client_entries

        return super().update(instance, validated_data)

    # -------------------------------------------------------
    # Output: return client[] as c_* keys ONLY
    # -------------------------------------------------------
    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request")
        media_url = getattr(settings, "MEDIA_URL", "/media/")
        parent_drone_type = data.get("drone_type")

        client_entries = data.get("client") or []
        transformed = []

        for entry in client_entries:
            entry = dict(entry or {})

            # optional drone_type fallback for display
            if not entry.get("drone_type"):
                entry["drone_type"] = parent_drone_type

            # convert stored relative path -> full URL (do not rewrite DB)
            att = entry.get("attachment")
            if att and isinstance(att, str) and not att.startswith("http"):
                rel = att.lstrip("/")
                url = f"{media_url.rstrip('/')}/{rel}"
                entry["attachment"] = request.build_absolute_uri(url) if request else url

            transformed.append(
                {
                    "c_model_name": entry.get("model_name"),
                    "c_drone_type": entry.get("drone_type"),
                    "c_uin_number": entry.get("uin_number"),
                    "c_drone_serial_number": entry.get("drone_serial_number"),
                    "c_flight_controller_serial_number": entry.get(
                        "flight_controller_serial_number"
                    ),
                    "c_remote_controller": entry.get("remote_controller"),
                    "c_battery_charger_serial_number": entry.get(
                        "battery_charger_serial_number"
                    ),
                    "c_battery_serial_number_1": entry.get("battery_serial_number_1"),
                    "c_battery_serial_number_2": entry.get("battery_serial_number_2"),
                    "c_attachment": entry.get("attachment"),
                }
            )

        data["client"] = transformed
        return data
