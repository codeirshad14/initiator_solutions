"""IndexNow: tell Bing (and Copilot / ChatGPT search, which use Bing) right away
when a product, service or blog page is saved. Google does not use IndexNow.

Enabled from admin: Site SEO Settings -> IndexNow. The key file is served by
views.indexnow_key_file at /<key>.txt.
"""
import json
import logging
import threading
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse

from django.conf import settings
from django.db import OperationalError, ProgrammingError, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Blog, Product, Service, SiteSEO

logger = logging.getLogger('web2.errors')

INDEXNOW_ENDPOINT = 'https://api.indexnow.org/indexnow'


def _send(site_seo_id, payload):
    data = json.dumps(payload).encode('utf-8')
    req = urlrequest.Request(
        INDEXNOW_ENDPOINT,
        data=data,
        headers={'Content-Type': 'application/json; charset=utf-8'},
        method='POST',
    )
    try:
        with urlrequest.urlopen(req, timeout=10) as response:
            status = f'OK: HTTP {response.status}'
    except HTTPError as error:
        # 403 = key file not reachable, 422 = URL does not belong to host.
        status = f'Failed: HTTP {error.code}'
    except (URLError, OSError) as error:
        status = f'Failed: {error}'
    if status.startswith('Failed'):
        logger.warning('IndexNow ping %s for %s', status, payload['urlList'])
    message = f'{timezone.now():%Y-%m-%d %H:%M} {status} {payload["urlList"][0]}'
    # update() keeps SiteSEO.updated_at unchanged.
    SiteSEO.objects.filter(pk=site_seo_id).update(indexnow_last_status=message[:255])


def _dispatch(site_seo_id, payload):
    threading.Thread(target=_send, args=(site_seo_id, payload), daemon=True).start()


def ping_indexnow(paths):
    """Queue an IndexNow ping for site paths like '/web2/blog/x/'. Returns True if queued."""
    if settings.DEBUG:
        return False
    try:
        site_seo = SiteSEO.objects.first()
    except (OperationalError, ProgrammingError):
        return False
    if not site_seo or not site_seo.indexnow_enabled or not site_seo.indexnow_key or not site_seo.robots_allow:
        return False

    base = site_seo.site_domain.rstrip('/')
    if not urlparse(base).netloc:
        return False
    payload = {
        'host': urlparse(base).netloc,
        'key': site_seo.indexnow_key,
        'keyLocation': f'{base}/{site_seo.indexnow_key}.txt',
        'urlList': [f'{base}{path}' for path in paths],
    }
    transaction.on_commit(lambda: _dispatch(site_seo.pk, payload))
    return True


@receiver(post_save, sender=Product)
@receiver(post_save, sender=Service)
@receiver(post_save, sender=Blog)
def ping_saved_page(sender, instance, raw=False, **kwargs):
    # Also pinged when unpublished, so Bing re-crawls and drops the page.
    if raw:
        return
    try:
        ping_indexnow([instance.get_absolute_url()])
    except Exception:
        logger.exception('IndexNow ping could not be queued for %r', instance)
