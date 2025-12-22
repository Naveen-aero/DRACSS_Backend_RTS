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

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny

from .models import SupportThread, SupportMessage
from .serializers import SupportThreadSerializer, SupportMessageSerializer


class SupportThreadViewSet(viewsets.ModelViewSet):
    serializer_class = SupportThreadSerializer
    permission_classes = [AllowAny]  # 🔥 no auth required
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.is_staff:
            return SupportThread.objects.all()
        elif user.is_authenticated:
            return SupportThread.objects.filter(created_by=user)
        else:
            return SupportThread.objects.none()  # anonymous sees nothing

    def perform_create(self, serializer):
        # Save created_by if user is logged in, else NULL
        serializer.save(created_by=self.request.user if self.request.user.is_authenticated else None)

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="messages",
        permission_classes=[AllowAny],
        parser_classes=[MultiPartParser, FormParser, JSONParser]
    )
    def messages(self, request, pk=None):
        thread = self.get_object()

        if thread.status == "CLOSED":
            return Response({"detail": "Ticket is closed"}, status=400)

        if request.method == "GET":
            messages = thread.messages.all()
            return Response(SupportMessageSerializer(messages, many=True).data)

        # POST message (allow anonymous)
        msg = SupportMessage.objects.create(
            thread=thread,
            sender=request.user if request.user.is_authenticated else None,
            message=request.data.get("message", ""),
            attachment=request.data.get("attachment")
        )

        thread.save(update_fields=["updated_at"])
        return Response(SupportMessageSerializer(msg).data, status=201)

    @action(
        detail=True,
        methods=["post"],
        url_path="close",
        permission_classes=[permissions.IsAdminUser]
    )
    def close_ticket(self, request, pk=None):
        thread = self.get_object()
        thread.status = "CLOSED"
        thread.save(update_fields=["status"])
        return Response({"status": "Ticket closed"})
