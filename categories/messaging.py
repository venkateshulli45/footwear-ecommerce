"""Deliver email, SMS, and web push for Notification rows (source of truth)."""

from __future__ import annotations

import json
import logging
from urllib.parse import urljoin

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import Notification, PushSubscription

logger = logging.getLogger(__name__)


def _absolute_url(link: str) -> str:
    if not link:
        return settings.SITE_PUBLIC_URL or '/'
    if link.startswith('http://') or link.startswith('https://'):
        return link
    base = (settings.SITE_PUBLIC_URL or '').rstrip('/')
    if not base:
        return link if link.startswith('/') else f'/{link}'
    path = link if link.startswith('/') else f'/{link}'
    return urljoin(f'{base}/', path.lstrip('/'))


def _email_ready() -> bool:
    if not getattr(settings, 'NOTIFICATION_EMAIL', True):
        return False
    if settings.DEBUG and 'console' in (settings.EMAIL_BACKEND or ''):
        return True
    return bool(getattr(settings, 'EMAIL_HOST', ''))


def _sms_ready() -> bool:
    if not getattr(settings, 'NOTIFICATION_SMS', False):
        return False
    return all(
        (
            getattr(settings, 'TWILIO_ACCOUNT_SID', ''),
            getattr(settings, 'TWILIO_AUTH_TOKEN', ''),
            getattr(settings, 'TWILIO_FROM_NUMBER', ''),
        )
    )


def _push_ready() -> bool:
    if not getattr(settings, 'NOTIFICATION_WEB_PUSH', True):
        return False
    return bool(
        getattr(settings, 'VAPID_PUBLIC_KEY', '')
        and getattr(settings, 'VAPID_PRIVATE_KEY', '')
    )


def _sms_destination_for(notification: Notification) -> str | None:
    order = notification.related_order
    if not order:
        return None
    phone = (getattr(order, 'phone', None) or '').strip()
    return phone or None


def deliver_notification_channels(notification: Notification) -> None:
    """Send configured channels for one in-app notification (idempotent per send attempt)."""
    user = notification.user
    ctx = {
        'notification': notification,
        'absolute_link': _absolute_url(notification.link or ''),
        'site_name': 'Jagam Footwear',
    }

    if _email_ready() and user.email:
        try:
            subject = notification.title[:200]
            text_body = render_to_string('emails/notification.txt', ctx)
            html_body = render_to_string('emails/notification.html', ctx)
            send_mail(
                subject,
                text_body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_body,
                fail_silently=False,
            )
        except Exception:
            logger.exception('notification email failed user=%s pk=%s', user.pk, notification.pk)

    if _sms_ready():
        to = _sms_destination_for(notification)
        if to:
            try:
                from twilio.rest import Client

                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                body = f'{notification.title}\n{(notification.body or "")[:280]}'
                client.messages.create(
                    to=to,
                    from_=settings.TWILIO_FROM_NUMBER,
                    body=body[:1600],
                )
            except Exception:
                logger.exception('notification sms failed user=%s pk=%s', user.pk, notification.pk)

    if _push_ready():
        _send_web_push(notification, ctx['absolute_link'])


def _send_web_push(notification: Notification, open_url: str) -> None:
    from pywebpush import WebPushException, webpush

    payload = json.dumps(
        {
            'title': notification.title[:120],
            'body': (notification.body or '')[:240],
            'url': open_url,
        }
    )
    subs = list(PushSubscription.objects.filter(user=notification.user))
    vapid_claims = {'sub': settings.VAPID_ADMIN_EMAIL}
    stale_ids: list[int] = []

    for sub in subs:
        subscription_info = {
            'endpoint': sub.endpoint,
            'keys': {'p256dh': sub.p256dh, 'auth': sub.auth},
        }
        try:
            webpush(
                subscription_info=subscription_info,
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims=vapid_claims,
            )
        except WebPushException as e:
            status = getattr(e.response, 'status_code', None) if getattr(e, 'response', None) else None
            if status in (404, 410):
                stale_ids.append(sub.pk)
            else:
                logger.warning(
                    'web push failed sub=%s notification=%s status=%s',
                    sub.pk,
                    notification.pk,
                    status,
                )
        except Exception:
            logger.exception('web push error sub=%s notification=%s', sub.pk, notification.pk)

    if stale_ids:
        PushSubscription.objects.filter(pk__in=stale_ids).delete()
