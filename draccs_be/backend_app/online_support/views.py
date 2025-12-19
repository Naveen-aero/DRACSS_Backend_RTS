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


from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import SupportThread, SupportMessage
from .serializers import SupportThreadSerializer, SupportMessageSerializer


class IsOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.created_by == request.user


class SupportThreadViewSet(viewsets.ModelViewSet):
    serializer_class = SupportThreadSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return SupportThread.objects.all()
        return SupportThread.objects.filter(created_by=user)

    def perform_create(self, serializer):
        # Automatically assign the logged-in user as ticket creator
        serializer.save(created_by=self.request.user)

    # -----------------------------
    # Messages under ticket
    # -----------------------------
    @action(detail=True, methods=["get", "post"], url_path="messages",
            parser_classes=[MultiPartParser, FormParser, JSONParser])
    def messages(self, request, pk=None):
        thread = self.get_object()

        if request.method == "GET":
            msgs = thread.messages.all()
            return Response(SupportMessageSerializer(msgs, many=True).data)

        if thread.status == "CLOSED":
            return Response({"detail": "Ticket is closed."}, status=status.HTTP_400_BAD_REQUEST)

        # POST new message
        msg = SupportMessage.objects.create(
            thread=thread,
            sender=request.user,
            message=request.data.get("message", ""),
            attachment=request.data.get("attachment")
        )

        # Mark ticket in progress if it was OPEN
        if thread.status == "OPEN":
            thread.status = "IN_PROGRESS"
            thread.save(update_fields=["status", "updated_at"])

        return Response(SupportMessageSerializer(msg).data, status=status.HTTP_201_CREATED)

    # -----------------------------
    # Close ticket
    # -----------------------------
    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        thread = self.get_object()
        thread.status = "CLOSED"
        thread.save(update_fields=["status", "updated_at"])
        return Response({"status": "Ticket closed"})
