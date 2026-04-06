from django.conf import settings
from django.db.models import Sum

from .models import BagItem, Notification


def bag_summary(request):
    count = 0
    if request.user.is_authenticated:
        agg = BagItem.objects.filter(user=request.user).aggregate(s=Sum('quantity'))
        count = agg['s'] or 0
    return {'bag_item_count': count}


def notification_preview(request):
    if not request.user.is_authenticated:
        return {
            'notification_unread_count': 0,
            'notification_preview': [],
        }
    base = Notification.objects.filter(user=request.user)
    return {
        'notification_unread_count': base.filter(read_at__isnull=True).count(),
        'notification_preview': list(base[:8]),
    }


def push_bootstrap(request):
    key = (getattr(settings, 'VAPID_PUBLIC_KEY', None) or '').strip()
    if not request.user.is_authenticated or not key:
        return {'vapid_public_key': ''}
    return {'vapid_public_key': key}
