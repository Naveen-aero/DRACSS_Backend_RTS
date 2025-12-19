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





from rest_framework import serializers
from .models import SupportThread, SupportMessage


class SupportMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(
        source="sender.username", read_only=True
    )

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
        read_only_fields = ["id", "sender", "created_at"]


class SupportThreadSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.username", read_only=True
    )
    assigned_to_name = serializers.CharField(
        source="assigned_to.username", read_only=True
    )

    class Meta:
        model = SupportThread
        fields = [
            "id",
            "subject",
            "status",
            "drone",
            "created_by",
            "created_by_name",
            "assigned_to",
            "assigned_to_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
        ]
