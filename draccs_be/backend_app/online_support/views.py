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

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import SupportThread, SupportMessage
from .serializers import (
    SupportThreadSerializer,
    SupportThreadListSerializer,
    SupportMessageSerializer,
)


class SupportThreadViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = SupportThread.objects.select_related("drone", "created_by", "assigned_to").order_by("-created_at")

        #  only prefetch messages when retrieving ONE thread (detail)
        if getattr(self, "action", None) == "retrieve":
            qs = qs.prefetch_related("messages")

        return qs

    def get_serializer_class(self):
        #  list endpoint uses lightweight serializer (no messages)
        if getattr(self, "action", None) == "list":
            return SupportThreadListSerializer
        return SupportThreadSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx


class SupportMessageViewSet(viewsets.ModelViewSet):
    serializer_class = SupportMessageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return SupportMessage.objects.select_related("sender", "thread").order_by("created_at")

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
