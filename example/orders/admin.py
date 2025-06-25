from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Order, OrderItem, Product


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ("subtotal",)
    fields = ("product", "quantity", "price", "subtotal")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "status",
        "total_amount",
        "created_at",
        "approved_at",
    )
    list_filter = ("status", "created_at", "approved_at")
    search_fields = ("id", "customer__username", "customer__email")
    readonly_fields = ("created_at", "updated_at", "approved_at", "order_items_display")
    inlines = [OrderItemInline]
    date_hierarchy = "created_at"
    actions = ["approve_orders"]

    def approve_orders(self, request, queryset):
        updated = 0
        for order in queryset.filter(status="pending"):
            order.approve()
            updated += 1
        self.message_user(request, f"{updated} orders were successfully approved.")

    approve_orders.short_description = "Approve selected orders"

    def order_items_display(self, obj):
        items = obj.items.all()
        if not items:
            return "No items"

        html = "<ul>"
        for item in items:
            html += f"<li>{item.quantity} x {item.product.name} (${item.price} each) = ${item.subtotal}</li>"
        html += "</ul>"
        return mark_safe(html)

    order_items_display.short_description = "Order Items"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")
