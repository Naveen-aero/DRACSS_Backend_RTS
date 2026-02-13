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
from rest_framework.permissions import IsAuthenticated
from .models import SupportThread, SupportMessage
from .serializers import (
    SupportThreadSerializer,
    SupportThreadListSerializer,
    SupportMessageSerializer,
)
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.db import transaction

User = get_user_model()


# -----------------------------
# Permissions
# -----------------------------
class IsStaffWriteReadOnly(BasePermission):
    """
    Allow read to all; only authenticated staff can modify (POST/PUT/DELETE)
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)


# -----------------------------
# Thread ViewSet
# -----------------------------
class SupportThreadViewSet(viewsets.ModelViewSet):
    queryset = SupportThread.objects.select_related("drone", "created_by", "assigned_to").order_by("-created_at")
 
    def get_permissions(self):
        if self.action in ["list", "retrieve", "create", "partial_update", "update"]:
            return [AllowAny()] 
        return [IsStaffWriteReadOnly()]


    def get_serializer_class(self):
        if self.action == "list":
            return SupportThreadListSerializer
        return SupportThreadSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        ticket = instance.ticket_id
        self.perform_destroy(instance)
        return Response(
            {"detail": f"Thread deleted successfully", "ticket_id": ticket},
            status=status.HTTP_200_OK
        )
    
    def perform_create(self, serializer):
        today = timezone.now().strftime("%Y%m%d")
        prefix = f"TKT-{today}"

        with transaction.atomic():
            last_thread = (
                SupportThread.objects
                .filter(ticket_id__startswith=prefix)
                .order_by("-ticket_id")
                .first()
            )

            if last_thread:
                last_number = int(last_thread.ticket_id[-2:])
                next_number = last_number + 1
            else:
                next_number = 1

            ticket_id = f"{prefix}{next_number:02d}"

            serializer.save(ticket_id=ticket_id)



# -----------------------------
# Message ViewSet
# -----------------------------
class SupportMessageViewSet(viewsets.ModelViewSet):
    queryset = SupportMessage.objects.all()
    serializer_class = SupportMessageSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "create"]:
            return [AllowAny()]

        if self.action in ["partial_update", "update", "destroy"]:
            return [IsAuthenticated()]  #  allow PATCH & DELETE

        return [IsStaffWriteReadOnly()]


    def get_queryset(self):
        thread_id = self.request.query_params.get("thread")
        if thread_id:
            return self.queryset.filter(thread_id=thread_id).select_related("thread", "sender").order_by("created_at")
        #  return all messages if thread_id is not specified
        return self.queryset.select_related("thread", "sender").order_by("created_at")



    def list(self, request, *args, **kwargs):
        thread_id = request.query_params.get("thread")
        qs = self.get_queryset()
        
        if not thread_id:
            # Return messages of latest thread
            latest_thread = SupportThread.objects.order_by("-created_at").first()
            if latest_thread:
                qs = qs.filter(thread_id=latest_thread.id)
        
        grouped = OrderedDict()
        for msg in qs:
            tid = msg.thread_id
            if tid not in grouped:
                grouped[tid] = {"id": tid, "attachment": None, "replies": []}
            grouped[tid]["replies"].append({
                "id": msg.id,
                "ui_id": None,
                "sender_name": msg.sender_name or (msg.sender.username if msg.sender else "support_guest"),
                "message": msg.message,
                "attachment": msg.attachment.url if msg.attachment else None,
                "created_at": msg.created_at,
            })
        return Response(list(grouped.values()))



    def perform_create(self, serializer):
        request = self.request
        sender_type = request.data.get("sender_type", "").lower()
        thread_id = request.data.get("thread")

        thread = None
        if thread_id:
            try:
                thread = SupportThread.objects.get(id=thread_id)
            except SupportThread.DoesNotExist:
                pass

        #  BD Team message
        if sender_type == "bdteam":
            serializer.save(
                sender=request.user if request.user.is_authenticated else None,
                sender_name="BDTeam"   #  fixed value
            )
        else:
            sender_name = (
                request.user.username if request.user.is_authenticated
                else (thread.created_by.username if thread and thread.created_by else "support_guest")
            )
            serializer.save(
                sender=request.user if request.user.is_authenticated else None,
                sender_name=sender_name
            )



    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        mid = instance.id
        self.perform_destroy(instance)
        return Response(
            {"detail": "Message deleted successfully", "message_db_id": mid},
            status=status.HTTP_200_OK
        )
