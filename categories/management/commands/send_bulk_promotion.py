"""Create a promotion Notification for every active user (email/SMS/push follow from signals)."""

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from categories.models import Notification
from categories.notifications import notify


class Command(BaseCommand):
    help = (
        'Send a promotion to all active users by creating one Notification per user. '
        'Outbound email/SMS/web push run after each save (use screen/tmux for large sends).'
    )

    def add_arguments(self, parser):
        parser.add_argument('--title', required=True, help='Notification title (shown in-app and email subject).')
        parser.add_argument('--body', default='', help='Optional body text.')
        parser.add_argument('--link', default='/', help='Relative or absolute link (default /).')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print usernames only; do not create notifications.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Max users to process (0 = no limit).',
        )

    def handle(self, *args, **options):
        qs = User.objects.filter(is_active=True).order_by('id')
        lim = options['limit']
        if lim > 0:
            qs = qs[:lim]
        n_done = 0
        for user in qs.iterator(chunk_size=200):
            if options['dry_run']:
                self.stdout.write(f'Would notify {user.username} ({user.email or "no email"})')
            else:
                notify(
                    user,
                    kind=Notification.Kind.PROMOTION,
                    title=options['title'][:255],
                    body=(options['body'] or '')[:4000],
                    link=(options['link'] or '/')[:500],
                )
            n_done += 1
        verb = 'Would process' if options['dry_run'] else 'Processed'
        self.stdout.write(self.style.SUCCESS(f'{verb} {n_done} user(s).'))
