from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("products/", views.product_list, name="product_list"),
    path("create/", views.create_order, name="create_order"),
    path("list/", views.order_list, name="order_list"),
    path("<int:order_id>/", views.order_detail, name="order_detail"),
    path("<int:order_id>/approve/", views.approve_order, name="approve_order"),
]
