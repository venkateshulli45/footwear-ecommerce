"""Serve PWA assets at fixed URLs (service worker scope must cover the site)."""

from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404


def service_worker(_request):
    path = Path(settings.BASE_DIR) / 'static' / 'pwa' / 'sw.js'
    if not path.is_file():
        raise Http404()
    resp = FileResponse(path.open('rb'), content_type='application/javascript; charset=utf-8')
    resp['Cache-Control'] = 'no-cache'
    return resp


def webmanifest(_request):
    path = Path(settings.BASE_DIR) / 'static' / 'pwa' / 'manifest.webmanifest'
    if not path.is_file():
        raise Http404()
    return FileResponse(
        path.open('rb'),
        content_type='application/manifest+json; charset=utf-8',
    )
