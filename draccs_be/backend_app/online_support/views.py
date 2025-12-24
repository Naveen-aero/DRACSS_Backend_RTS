# from rest_framework import viewsets, permissions
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# from .models import SupportThread, SupportMessage
# from .serializers import SupportThreadSerializer, SupportMessageSerializer


# class IsThreadOwnerOrStaff(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return request.user.is_staff or obj.created_by_id == request.user.id


# class SupportThreadViewSet(viewsets.ModelViewSet):
#     serializer_class = SupportThreadSerializer
#     permission_classes = [permissions.IsAuthenticated, IsThreadOwnerOrStaff]
#     parser_classes = [MultiPartParser, FormParser, JSONParser]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff:
#             return SupportThread.objects.all()
#         return SupportThread.objects.filter(created_by=user)

#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user)

#     # /api/support/threads/{id}/messages/
#     @action(detail=True, methods=["get", "post"], url_path="messages",
#             parser_classes=[MultiPartParser, FormParser, JSONParser])
#     def messages(self, request, pk=None):
#         thread = self.get_object()

#         if request.method == "GET":
#             msgs = thread.messages.all()
#             return Response(SupportMessageSerializer(msgs, many=True).data)

#         # POST message
#         ser = SupportMessageSerializer(data=request.data)
#         ser.is_valid(raise_exception=True)

#         msg = SupportMessage.objects.create(
#             thread=thread,
#             sender=request.user,
#             message=ser.validated_data.get("message", ""),
#             attachment=ser.validated_data.get("attachment", None),
#         )

#         # update thread timestamp
#         thread.save(update_fields=["updated_at"])

#         return Response(SupportMessageSerializer(msg).data, status=201)

from collections import OrderedDict

from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.permissions import BasePermission, SAFE_METHODS, AllowAny
from rest_framework.response import Response

from .models import SupportThread, SupportMessage
from .serializers import (
    SupportThreadSerializer,
    SupportThreadListSerializer,
    SupportMessageSerializer,
)

User = get_user_model()


#  Permission: allow read to all, but only STAFF can delete threads/messages
# (If you want any logged-in user to delete, tell me — change is 1 line.)
class IsStaffWriteReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class SupportThreadViewSet(viewsets.ModelViewSet):
    #  Keeps GET open, protects DELETE/PATCH/PUT/POST
    permission_classes = [IsStaffWriteReadOnly]

    def get_queryset(self):
        qs = SupportThread.objects.select_related("drone", "created_by", "assigned_to").order_by("-created_at")
        if getattr(self, "action", None) == "retrieve":
            qs = qs.prefetch_related("messages")
        return qs

    def get_serializer_class(self):
        if getattr(self, "action", None) == "list":
            return SupportThreadListSerializer
        return SupportThreadSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    #  Optional: clean response after delete
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        ticket = instance.ticket_id
        self.perform_destroy(instance)
        return Response(
            {"detail": f"Thread deleted successfully", "ticket_id": ticket},
            status=status.HTTP_200_OK
        )


class SupportMessageViewSet(viewsets.ModelViewSet):
    serializer_class = SupportMessageSerializer

    #  Keep your existing behavior: allow guest POST
    # BUT: delete of messages should be restricted (staff)
    def get_permissions(self):
        # anyone can GET + POST (your requirement)
        if self.action in ["list", "retrieve", "create"]:
            return [AllowAny()]
        # only staff can update/delete messages
        return [IsStaffWriteReadOnly()]

    def get_queryset(self):
        return SupportMessage.objects.select_related("sender", "thread").order_by("thread_id", "created_at")

    def list(self, request, *args, **kwargs):
        """
        GET /api/messages/ grouped by thread.
        - Top-level "id" is sequential per thread group: 1,2,3...
        - Each reply has "id" sequential inside its thread: 1,2,3...
        """
        qs = self.filter_queryset(self.get_queryset())

        grouped = OrderedDict()

        # Group messages by thread
        for msg in qs:
            tid = msg.thread_id

            if tid not in grouped:
                grouped[tid] = {
                    "thread": tid,
                    "attachment": None,
                    "replies": []
                }

            grouped[tid]["replies"].append({
                "sender_name": msg.sender.username if msg.sender else None,
                "message": msg.message,
                "attachment": msg.attachment.url if msg.attachment else None,
                "created_at": msg.created_at,
            })

        # Build final response with sequential ids
        response = []
        group_id = 1

        for tid, group in grouped.items():
            for i, reply in enumerate(group["replies"], start=1):
                reply["id"] = i

            response.append({
                "id": group_id,
                "thread": group["thread"],
                "attachment": group["attachment"],
                "replies": group["replies"],
            })
            group_id += 1

        return Response(response)

    def perform_create(self, serializer):
        """
        If logged in: sender = request.user
        If not logged in: sender = support_guest (or None)
        """
        user = getattr(self.request, "user", None)

        if user and user.is_authenticated:
            serializer.save(sender=user)
            return

        guest = User.objects.filter(username="support_guest").first()
        serializer.save(sender=guest)

    #  Optional: clean response after delete
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        mid = instance.id
        self.perform_destroy(instance)
        return Response(
            {"detail": "Message deleted successfully", "message_db_id": mid},
            status=status.HTTP_200_OK
        )
