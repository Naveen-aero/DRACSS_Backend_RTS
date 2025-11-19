# draccs_be/backend_app/orderform/views.py

from rest_framework import generics
from .models import ChecklistItem, Order, OrderItem
from .serializers import ChecklistItemSerializer, OrderSerializer, OrderItemSerializer


# -------- TEMPLATE ENDPOINT (READ-ONLY) --------
class ChecklistItemListView(generics.ListAPIView):
    """
    GET /api/checklist-items/
    Returns the standard Bhumi A10E checklist template.
    """
    queryset = ChecklistItem.objects.all().order_by("sort_order")
    serializer_class = ChecklistItemSerializer


# -------- ORDERS (WHERE MODIFIED CHECKLIST IS STORED) --------
class OrderListCreateView(generics.ListCreateAPIView):
    """
    GET /api/orders/    -> list all orders
    POST /api/orders/   -> create new order
                          If 'items' missing, auto-copy from ChecklistItem.
    """
    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/orders/<id>/    -> order + its items
    PUT/PATCH /api/orders/<id>/ -> update header and (optionally) items
    DELETE /api/orders/<id>/ -> delete order and its items
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


# -------- INDIVIDUAL ORDER ITEMS (for add/delete per-line) --------
class OrderItemCreateView(generics.CreateAPIView):
    """
    POST /api/order-items/
    Body should include: order, description, quantity_ordered, ...
    Used to ADD new line items (extra accessories, etc.).
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class OrderItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/order-items/<id>/
    PATCH/PUT /api/order-items/<id>/  -> edit one line (change qty, tick, remarks)
    DELETE /api/order-items/<id>/     -> delete one line from order.
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
