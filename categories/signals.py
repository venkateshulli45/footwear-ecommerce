from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from . import notifications as notification_service
from .models import Notification, Order


@receiver(pre_save, sender=Order)
def order_cache_state_for_notifications(sender, instance, **kwargs):
    instance._notif_prev = None
    if not instance.pk:
        return
    try:
        old = Order.objects.get(pk=instance.pk)
        instance._notif_prev = (old.status, old.payment_status)
    except Order.DoesNotExist:
        pass


@receiver(post_save, sender=Order)
def order_emit_notifications(sender, instance, created, **kwargs):
    if created:
        notification_service.notify_order_placed(instance)
        return

    prev = getattr(instance, '_notif_prev', None)
    if not prev:
        return

    prev_status, prev_payment = prev
    if prev_status != instance.status:
        notification_service.notify_order_status_change(instance, prev_status)
    if (
        prev_payment != instance.payment_status
        and instance.payment_status == Order.PaymentStatus.PAID
    ):
        notification_service.notify_payment_received(instance)


@receiver(post_save, sender=Notification)
def notification_deliver_outbound(sender, instance, created, **kwargs):
    if not created:
        return
    pk = instance.pk

    def _run():
        from .messaging import deliver_notification_channels

        try:
            n = Notification.objects.get(pk=pk)
        except Notification.DoesNotExist:
            return
        deliver_notification_channels(n)

    transaction.on_commit(_run)
