"""Create in-app notifications for storefront users."""

from __future__ import annotations

from django.contrib.auth.models import User
from django.utils import timezone

from .models import Notification, Order


def notify(
    user: User,
    *,
    kind: str,
    title: str,
    body: str = '',
    link: str = '',
    related_order: Order | None = None,
) -> Notification:
    return Notification.objects.create(
        user=user,
        kind=kind,
        title=title[:255],
        body=(body or '')[:4000],
        link=(link or '')[:500],
        related_order=related_order,
    )


def notify_order_placed(order: Order) -> None:
    notify(
        order.user,
        kind=Notification.Kind.ORDER,
        title='Order confirmed',
        body=f'Order {order.order_number} was placed. Total ₹{order.total}. We’ll email updates as it moves.',
        link=_order_history_fragment(order),
        related_order=order,
    )


def notify_order_status_change(order: Order, previous_status: str) -> None:
    labels = {
        Order.Status.PENDING_PAYMENT: 'Pending payment',
        Order.Status.CONFIRMED: 'Confirmed',
        Order.Status.PROCESSING: 'Processing',
        Order.Status.SHIPPED: 'Shipped',
        Order.Status.DELIVERED: 'Delivered',
        Order.Status.CANCELLED: 'Cancelled',
    }
    new_label = labels.get(order.status, order.status)
    titles = {
        Order.Status.PROCESSING: 'Order is being prepared',
        Order.Status.SHIPPED: 'Order shipped',
        Order.Status.DELIVERED: 'Order delivered',
        Order.Status.CANCELLED: 'Order cancelled',
        Order.Status.PENDING_PAYMENT: 'Payment pending',
        Order.Status.CONFIRMED: 'Order confirmed',
    }
    title = titles.get(order.status, f'Order update: {new_label}')
    body = f'Order {order.order_number} is now {new_label.lower()}.'
    notify(
        order.user,
        kind=Notification.Kind.ORDER,
        title=title,
        body=body,
        link=_order_history_fragment(order),
        related_order=order,
    )


def notify_payment_received(order: Order) -> None:
    notify(
        order.user,
        kind=Notification.Kind.ORDER,
        title='Payment received',
        body=f'We recorded payment for order {order.order_number}.',
        link=_order_history_fragment(order),
        related_order=order,
    )


def _order_history_fragment(order: Order) -> str:
    from django.urls import reverse

    return f'{reverse("order_history")}#order-{order.pk}'
