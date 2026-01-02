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


# -----------------------
# Messages
# -----------------------
class SupportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = ["id", "thread", "message", "attachment", "sender_name", "created_at"]
        read_only_fields = ["id", "created_at"]

   
  


class SupportMessageBriefSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(read_only=True)

    class Meta:
        model = SupportMessage
        fields = ["id", "sender_name", "message", "attachment", "created_at"]
        read_only_fields = fields


# -----------------------
# Threads
# -----------------------
class SupportThreadListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    drone_serial_number = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SupportThread
        fields = [
            "id",
            "ticket_id",
            "subject",
            "status",
            "drone_serial_number",
            "created_by_name",
            "assigned_to",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_drone_serial_number(self, obj):
        if not obj.drone_id:
            return None
        return getattr(obj.drone, "drone_serial_number", None)


class SupportThreadSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    drone_serial_number = serializers.SerializerMethodField(read_only=True)
    drone_serial_number_input = serializers.CharField(write_only=True, required=True)
    messages = SupportMessageBriefSerializer(many=True, read_only=True)

    class Meta:
        model = SupportThread
        fields = [
            "id",
            "ticket_id",
            "subject",
            "status",
            "drone_serial_number",
            "drone_serial_number_input",
            "created_by_name",
            "assigned_to",
            "created_at",
            "updated_at",
            "messages",
        ]
        read_only_fields = [
            "id", "ticket_id", "drone_serial_number", "created_by_name",
            "created_at", "updated_at", "messages"
        ]

    def get_drone_serial_number(self, obj):
        if not obj.drone_id:
            return None
        return getattr(obj.drone, "drone_serial_number", None)

    def to_internal_value(self, data):
        data = data.copy()
        if "drone_serial_number" in data and "drone_serial_number_input" not in data:
            data["drone_serial_number_input"] = data.get("drone_serial_number")
        return super().to_internal_value(data)

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

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data.pop("drone_serial_number_input", None)
        validated_data["drone"] = getattr(self, "_resolved_drone", None)

        if request.user and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        else:
            guest_name = request.data.get("created_by_name", "support_guest")
            user, _ = User.objects.get_or_create(username=guest_name, defaults={"is_active": False})
            validated_data["created_by"] = user

        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "drone_serial_number_input" in validated_data:
            validated_data.pop("drone_serial_number_input", None)
            instance.drone = getattr(self, "_resolved_drone", instance.drone)
        return super().update(instance, validated_data)
