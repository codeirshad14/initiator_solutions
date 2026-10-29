"""Read-only health check of the live database, for use right after a deploy.

    python manage.py check_site_data

Renders every public page the way a visitor would and reports pages that crash,
missing image files, and data that would break links or the layout. It never
changes data. Exit code is 1 when an ERROR is found, so it can gate a deploy.
"""
import re
import traceback
from urllib.parse import urlparse

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.http.request import validate_host
from django.test import Client
from django.urls import reverse

from web2.models import (
    AboutUSModel, Blog, CatalogGroup, Lan_AboutusModel, Lan_PageBanModel, PortfolioModel, Product, Service, SiteSEO,
)

SLUG_RE = re.compile(r'^[-a-zA-Z0-9_]+$')
STATIC_PAGES = (
    'index', 'aboutus', 'portfolio', 'contact', 'web_product', 'web_dev', 'our_module_services', 'homeblog',
    'robots_txt', 'sitemap_xml', 'llms_txt',
)


class Command(BaseCommand):
    help = 'Check the database for content that would crash or break pages (read-only).'

    def handle(self, *args, **options):
        self.errors = 0
        self.warnings = 0
        site_seo = self.check_site_seo()
        self.client = Client(HTTP_HOST=self.pick_host(site_seo))

        self.section('Groups')
        for group in CatalogGroup.objects.all():
            if not SLUG_RE.match(group.slug or ''):
                self.error(f'{group.get_group_type_display()} group "{group.name}" has an invalid slug "{group.slug}"; its pages cannot be opened.')

        self.section('Pages')
        for name in STATIC_PAGES:
            self.check_url(reverse(name), name)
        for model, label in ((Product, 'Product'), (Service, 'Service'), (Blog, 'Blog')):
            for item in model.objects.filter(is_published=True):
                title = getattr(item, 'name', '') or getattr(item, 'title', '') or f'#{item.pk}'
                try:
                    url = item.get_absolute_url()
                except Exception as exc:
                    self.error(f'{label} "{title}" (id {item.pk}): link cannot be built: {exc}')
                    continue
                self.check_url(url, f'{label} "{title}"')
                if model is Service and item.show_on_module_page and not item.module_group_id:
                    self.warn(f'Service "{title}" is ticked for Our Modules but has no Module group; it shows without a group filter.')

        self.section('Images')
        self.check_images(Product.objects.filter(is_published=True), 'img', 'Product')
        self.check_images(Service.objects.filter(is_published=True), 'img', 'Service')
        self.check_images(Blog.objects.filter(is_published=True), 'image', 'Blog')
        self.check_images(Lan_PageBanModel.objects.all(), 'img', 'Home banner')
        self.check_images(Lan_AboutusModel.objects.all(), 'img', 'Home about')
        self.check_images(PortfolioModel.objects.all(), 'img', 'Portfolio')

        self.section('Home page content')
        if not Lan_PageBanModel.objects.exists():
            self.error('No home banner record: the home page has no H1 heading and no hero. Add one under "Lan page ban models".')
        for about in Lan_AboutusModel.objects.all():
            for field in ('client', 'project', 'emp', 'hrs'):
                value = (getattr(about, field) or '').strip()
                if value and not value.isdigit():
                    self.warn(f'Home counter "{field}" is "{value}"; use numbers only or the counter shows 0.')
        if not AboutUSModel.objects.exists():
            self.warn('Who We Are page has no content records.')

        summary = f'{self.errors} error(s), {self.warnings} warning(s)'
        if self.errors:
            raise CommandError(f'Site data check finished: {summary}.')
        self.stdout.write(self.style.SUCCESS(f'\nSite data check passed: {summary}.'))

    def section(self, title):
        self.stdout.write(f'\n== {title}')

    def error(self, message):
        self.errors += 1
        self.stdout.write(self.style.ERROR(f'  ERROR    {message}'))

    def warn(self, message):
        self.warnings += 1
        self.stdout.write(self.style.WARNING(f'  WARNING  {message}'))

    def ok(self, message):
        self.stdout.write(f'  ok       {message}')

    def check_site_seo(self):
        self.section('Site SEO settings')
        site_seo = SiteSEO.objects.first()
        if site_seo is None:
            self.warn('No Site SEO Settings record; defaults are used. Add one in admin.')
            return None
        if not urlparse(site_seo.site_domain or '').netloc:
            self.error(f'Site domain "{site_seo.site_domain}" is not a full URL like https://www.initiatorsolutions.com.')
        if not site_seo.robots_allow:
            self.warn('"Robots allow" is OFF: search engines are blocked from the whole site.')
        if len(site_seo.default_title) > 60:
            self.warn(f'Home title is {len(site_seo.default_title)} characters (aim for 60 or less).')
        if len(site_seo.default_description) > 160:
            self.warn(f'Home description is {len(site_seo.default_description)} characters (aim for 155 or less).')
        self.ok(f'{site_seo.organization_name} / {site_seo.site_domain}')
        return site_seo

    def pick_host(self, site_seo):
        candidates = [urlparse(site_seo.site_domain).netloc if site_seo else '']
        candidates += [host.lstrip('.') for host in settings.ALLOWED_HOSTS if host != '*']
        candidates.append('testserver')
        return next(host for host in candidates if host and validate_host(host, settings.ALLOWED_HOSTS or ['testserver']))

    def check_url(self, url, label):
        try:
            response = self.client.get(url, secure=True)
        except Exception as exc:
            where = traceback.extract_tb(exc.__traceback__)[-1]
            self.error(f'{label} {url} crashes: {type(exc).__name__}: {exc} ({where.filename.split("site-packages")[-1]}:{where.lineno})')
            return
        if response.status_code != 200:
            self.error(f'{label} {url} returns HTTP {response.status_code}')
        else:
            self.ok(f'{url}')

    def check_images(self, queryset, field, label):
        missing = 0
        for item in queryset:
            image = getattr(item, field)
            if image and not default_storage.exists(image.name):
                missing += 1
                title = getattr(item, 'name', '') or getattr(item, 'title', '') or getattr(item, 'imagalt', '') or f'#{item.pk}'
                self.warn(f'{label} "{title}": image file missing on server: {image.name} (the page shows "No Image").')
        if not missing:
            self.ok(f'{label} images present')
