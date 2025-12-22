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

from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import SupportThread, SupportMessage
from .serializers import SupportThreadSerializer, SupportMessageSerializer

User = get_user_model()

DEFAULT_GUEST_USERNAME = "support_guest"


def generate_ticket_id() -> str:
    today = timezone.localdate().strftime("%Y%m%d")
    seq = SupportThread.objects.filter(created_at__date=timezone.localdate()).count() + 1
    return f"TKT-{today}-{seq:04d}"


def get_guest_user():
    # create the guest user if it doesn't exist
    guest, _ = User.objects.get_or_create(
        username=DEFAULT_GUEST_USERNAME,
        defaults={"email": "support_guest@local", "is_active": True},
    )
    return guest


def resolve_user(request):
    # 1) logged-in user
    if getattr(request, "user", None) and request.user.is_authenticated:
        return request.user

    # 2) header
    user_id = request.headers.get("X-USER-ID")
    if user_id:
        try:
            return User.objects.get(id=int(user_id))
        except Exception:
            return None

    # 3) fallback guest
    return get_guest_user()


class SupportThreadViewSet(viewsets.ModelViewSet):
    queryset = SupportThread.objects.select_related("created_by", "assigned_to", "drone").all()
    serializer_class = SupportThreadSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        created_by = resolve_user(request)
        if created_by is None:
            return Response({"detail": "Invalid X-USER-ID."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            ticket_id = generate_ticket_id()
            thread = serializer.save(created_by=created_by, ticket_id=ticket_id)

        return Response(self.get_serializer(thread).data, status=status.HTTP_201_CREATED)


class SupportMessageViewSet(viewsets.ModelViewSet):
    queryset = SupportMessage.objects.select_related("thread", "sender").all()
    serializer_class = SupportMessageSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        thread_id = self.request.query_params.get("thread")
        if thread_id:
            qs = qs.filter(thread_id=thread_id)
        return qs

    def create(self, request, *args, **kwargs):
        sender = resolve_user(request)
        if sender is None:
            return Response({"detail": "Invalid X-USER-ID."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        msg = serializer.save(sender=sender)
        return Response(self.get_serializer(msg).data, status=status.HTTP_201_CREATED)
