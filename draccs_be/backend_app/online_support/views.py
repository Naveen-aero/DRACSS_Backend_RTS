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
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response

from .models import SupportThread, SupportMessage
from .serializers import (
    SupportThreadSerializer,
    SupportThreadListSerializer,
    SupportMessageSerializer,
)


User = get_user_model()


class SupportThreadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

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


class SupportMessageViewSet(viewsets.ModelViewSet):
    serializer_class = SupportMessageSerializer

    # Allow anyone to POST messages (guest + authenticated)
    permission_classes = [AllowAny]

    def get_queryset(self):
        return SupportMessage.objects.select_related("sender", "thread").order_by("thread_id", "created_at")

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())

        grouped = OrderedDict()

        for msg in qs:
            tid = msg.thread_id

            if tid not in grouped:
                grouped[tid] = {
                    "id": msg.id,
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

        return Response(list(grouped.values()))

    def perform_create(self, serializer):
        """
         If logged in: sender = request.user
         If not logged in: sender = support_guest (or None if guest user doesn't exist)
        """
        user = getattr(self.request, "user", None)

        if user and user.is_authenticated:
            serializer.save(sender=user)
            return

        guest = User.objects.filter(username="support_guest").first()
        serializer.save(sender=guest)
