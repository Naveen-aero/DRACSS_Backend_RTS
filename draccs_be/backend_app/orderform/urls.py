# draccs_be/backend_app/orderform/urls.py

from django.urls import path
from .views import (
    ChecklistItemListView,
    OrderListCreateView,
    OrderDetailView,
    OrderItemCreateView,
    OrderItemDetailView,
)

urlpatterns = [
    # Template checklist (read-only)
    path("api/checklist-items/", ChecklistItemListView.as_view(), name="checklist-items"),

    # Orders (editable instance of checklist)
    path("api/orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("api/orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),

    # Order items (add/delete/edit lines)
    path("api/order-items/", OrderItemCreateView.as_view(), name="orderitem-create"),
    path("api/order-items/<int:pk>/", OrderItemDetailView.as_view(), name="orderitem-detail"),
]
