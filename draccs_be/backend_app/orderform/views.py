from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ChecklistItem, Order, OrderItem
from .serializers import ChecklistItemSerializer, OrderSerializer


class ChecklistItemViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChecklistItemSerializer

    def get_queryset(self):
        qs = ChecklistItem.objects.all().order_by("sort_order", "id")
        drone_model = self.request.query_params.get("drone_model")
        if drone_model:
            qs = qs.filter(drone_model=drone_model)
        return qs


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all().order_by("-created_at")

    @action(detail=False, methods=["post"], url_path="create-from-standard")
    def create_from_standard(self, request):
        drone_model = request.data.get("drone_model", "Bhumi A10E")

        order_serializer = OrderSerializer(data={**request.data, "items": []})
        order_serializer.is_valid(raise_exception=True)
        order = order_serializer.save()

        templates = ChecklistItem.objects.filter(
            drone_model=drone_model
        ).order_by("sort_order", "id")

        for tmpl in templates:
            OrderItem.objects.create(
                order=order,
                checklist_item=tmpl,
                description=tmpl.description,
                quantity_ordered=tmpl.default_quantity,
                quantity_delivered=0,
                is_checked=False,
                is_from_template=True,
            )

        full_order = OrderSerializer(order)
        return Response(full_order.data, status=status.HTTP_201_CREATED)
