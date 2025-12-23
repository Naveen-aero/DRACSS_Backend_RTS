# from rest_framework import serializers
# from .models import SupportThread, SupportMessage


# class SupportMessageSerializer(serializers.ModelSerializer):
#     sender_name = serializers.CharField(source="sender.username", read_only=True)

#     class Meta:
#         model = SupportMessage
#         fields = ["id", "thread", "sender", "sender_name", "message", "attachment", "created_at"]
#         read_only_fields = ["id", "sender", "thread", "created_at"]


# class SupportThreadSerializer(serializers.ModelSerializer):
#     created_by_name = serializers.CharField(source="created_by.username", read_only=True)
#     assigned_to_name = serializers.CharField(source="assigned_to.username", read_only=True)
#     last_message = serializers.SerializerMethodField()

#     class Meta:
#         model = SupportThread
#         fields = [
#             "id", "subject", "status",
#             "created_by", "created_by_name",
#             "assigned_to", "assigned_to_name",
#             "drone",
#             "created_at", "updated_at",
#             "last_message",
#         ]
#         read_only_fields = ["id", "created_by", "created_at", "updated_at", "last_message"]

#     def get_last_message(self, obj):
#         msg = obj.messages.last()
#         if not msg:
#             return None
#         return {
#             "message": msg.message,
#             "sender": msg.sender.username,
#             "created_at": msg.created_at
#         }

from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import SupportThread, SupportMessage

DroneRegistration = apps.get_model("drone_registration", "DroneRegistration")
User = get_user_model()


class SupportMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = SupportMessage
        fields = [
            "id",
            "thread",
            "sender",
            "sender_name",
            "message",
            "attachment",
            "created_at",
        ]
        read_only_fields = ["id", "sender", "created_at", "sender_name"]


class SupportThreadSerializer(serializers.ModelSerializer):
    #  READ: show created_by username
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    #  READ: return drone_serial_number from the related drone FK
    drone_serial_number = serializers.SerializerMethodField(read_only=True)

    #  WRITE: accept drone serial number from client (but hide from response)
    drone_serial_number_input = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = SupportThread
        fields = [
            "id",
            "ticket_id",
            "subject",
            "status",

            # response key you want:
            "drone_serial_number",

            # internal write-only field:
            "drone_serial_number_input",

            "created_by_name",
            "assigned_to",

            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "ticket_id",
            "drone_serial_number",
            "created_by_name",
            "created_at",
            "updated_at",
        ]

    # ---- READ ----
    def get_drone_serial_number(self, obj):
        if not obj.drone_id:
            return None
        return getattr(obj.drone, "drone_serial_number", None)

    # ---- INPUT MAPPING ----
    def to_internal_value(self, data):
        """
        Allow client to POST using the key 'drone_serial_number'
        while internally we validate using 'drone_serial_number_input'.
        """
        data = data.copy()
        if "drone_serial_number" in data and "drone_serial_number_input" not in data:
            data["drone_serial_number_input"] = data.get("drone_serial_number")
        return super().to_internal_value(data)

    # ---- VALIDATION ----
    def validate_drone_serial_number_input(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("drone_serial_number is required")

        try:
            drone = DroneRegistration.objects.get(drone_serial_number=value)
        except DroneRegistration.DoesNotExist:
            raise serializers.ValidationError("No drone found with this drone_serial_number")

        self._resolved_drone = drone
        return value

    def _get_created_by_user(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            return user

        # fallback guest user
        try:
            return User.objects.get(username="support_guest")
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Guest user 'support_guest' not found. Create it or enable authentication."
            )

    # ---- CREATE / UPDATE ----
    def create(self, validated_data):
        request = self.context.get("request")

        # remove write-only serial input
        validated_data.pop("drone_serial_number_input", None)

        # attach FK
        validated_data["drone"] = getattr(self, "_resolved_drone", None)

        # server-side created_by
        validated_data["created_by"] = self._get_created_by_user(request)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "drone_serial_number_input" in validated_data:
            validated_data.pop("drone_serial_number_input", None)
            instance.drone = getattr(self, "_resolved_drone", instance.drone)

        return super().update(instance, validated_data)
