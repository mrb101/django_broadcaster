from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from django_broadcaster.events import CloudEvent
from django_broadcaster.publishers import publisher

from .models import Order, OrderItem, Product


def is_admin(user):
    """Check if user is an admin"""
    return user.is_staff or user.is_superuser


@login_required
def create_order(request):
    """
    View for creating a new order
    """
    if request.method == "POST":
        # Get selected products from the form
        product_ids = request.POST.getlist("products")
        quantities = request.POST.getlist("quantities")

        if not product_ids:
            messages.error(request, "Please select at least one product")
            return redirect("orders:product_list")

        # Create a new order
        order = Order.objects.create(
            customer=request.user,
            status="pending",
            total_amount=0,  # Will be calculated below
        )

        # Add products to the order
        total_amount = 0
        for i, product_id in enumerate(product_ids):
            product = get_object_or_404(Product, id=product_id)
            quantity = int(quantities[i]) if i < len(quantities) else 1

            # Create order item
            OrderItem.objects.create(
                order=order, product=product, quantity=quantity, price=product.price
            )

            # Update total amount
            total_amount += product.price * quantity

        # Update order total
        order.total_amount = total_amount
        order.save()

        # Dispatch order created event
        event = CloudEvent(
            event_type="order.created",
            source="/orders/create",
            data={
                "order_id": str(order.id),
                "customer_id": str(order.customer.id),
                "customer_email": order.customer.email,
                "total_amount": str(order.total_amount),
                "status": order.status,
            },
            subject=f"Order {order.id} created",
        )
        publisher.publish_cloud_event(event)

        # Send email notification to admin
        admin_emails = [admin[1] for admin in settings.ADMINS]
        if admin_emails:
            send_mail(
                subject=f"New Order #{order.id} Created",
                message=f"A new order (#{order.id}) has been created by {request.user.username} for ${order.total_amount}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=True,
            )

        messages.success(request, "Order created successfully")
        return redirect("orders:order_detail", order_id=order.id)

    # GET request - show form
    products = Product.objects.all()
    return render(request, "orders/create_order.html", {"products": products})


@login_required
def order_detail(request, order_id):
    """
    View for displaying order details
    """
    # For admins, get any order, for regular users, only their own orders
    if request.user.is_staff or request.user.is_superuser:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, customer=request.user)

    return render(request, "orders/order_detail.html", {"order": order})


@login_required
def order_list(request):
    """
    View for listing orders
    """
    # For admins, show all orders, for regular users, only their own orders
    if request.user.is_staff or request.user.is_superuser:
        orders = Order.objects.all().order_by("-created_at")
    else:
        orders = Order.objects.filter(customer=request.user).order_by("-created_at")

    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
@user_passes_test(is_admin)
@require_POST
def approve_order(request, order_id):
    """
    View for approving an order (admin only)
    """
    order = get_object_or_404(Order, id=order_id)

    if order.status != "pending":
        messages.error(
            request,
            f"Order #{order.id} cannot be approved because it is {order.status}",
        )
        return redirect("orders:order_detail", order_id=order.id)

    # Approve the order
    order.approve()

    # Dispatch order approved event
    event = CloudEvent(
        event_type="order.approved",
        source="/orders/approve",
        data={
            "order_id": str(order.id),
            "customer_id": str(order.customer.id),
            "customer_email": order.customer.email,
            "total_amount": str(order.total_amount),
            "status": order.status,
            "approved_at": order.approved_at.isoformat() if order.approved_at else None,
        },
        subject=f"Order {order.id} approved",
    )
    publisher.publish_cloud_event(event)

    # Send email notification to customer
    if order.customer.email:
        send_mail(
            subject=f"Your Order #{order.id} Has Been Approved",
            message=f"Good news! Your order (#{order.id}) has been approved and is being processed.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer.email],
            fail_silently=True,
        )

    messages.success(request, f"Order #{order.id} has been approved")
    return redirect("orders:order_detail", order_id=order.id)


def product_list(request):
    """
    View for listing products
    """
    products = Product.objects.all()
    return render(request, "orders/product_list.html", {"products": products})
