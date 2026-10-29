from urllib.parse import urlparse

from django.contrib.sitemaps import Sitemap
from django.db import OperationalError, ProgrammingError
from django.db.models import Max, Q
from django.urls import reverse

from .models import (
    AboutUSModel, AboutVisionModel, Blog, ContactModel, Lan_AboutusModel, Lan_PageBanModel,
    PortfolioModel, Product, Service, SiteSEO,
)


def _latest(queryset, field):
    return queryset.aggregate(latest=Max(field))['latest']


def _newest(*dates):
    dates = [date for date in dates if date]
    return max(dates) if dates else None


class CanonicalDomainSitemap(Sitemap):
    protocol = 'https'

    def _site_domain(self):
        try:
            site_seo = SiteSEO.objects.first()
        except (OperationalError, ProgrammingError):
            site_seo = None
        domain = site_seo.site_domain if site_seo else ''
        if not urlparse(domain or '').netloc:
            domain = 'https://www.initiatorsolutions.com'
        return domain.rstrip('/')

    def get_domain(self, site=None):
        parsed = urlparse(self._site_domain())
        return parsed.netloc or parsed.path

    def get_protocol(self, protocol=None):
        parsed = urlparse(self._site_domain())
        return parsed.scheme or 'https'

    def _canonical_items(self, queryset):
        # Pages whose canonical URL points elsewhere must not be in the sitemap.
        base = self._site_domain()
        return [
            item for item in queryset
            if not item.canonical_url
            or item.canonical_url.rstrip('/') == f'{base}{item.get_absolute_url()}'.rstrip('/')
        ]


class StaticViewSitemap(CanonicalDomainSitemap):
    changefreq = 'weekly'

    def items(self):
        return [
            'index',
            'homeblog',
            'contact',
            'aboutus',
            'portfolio',
            'web_product',
            'web_dev',
            'our_module_services',
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == 'index' else 0.7

    def lastmod(self, item):
        # Google only trusts lastmod when it reflects real content changes,
        # so each page uses the newest change of the content it shows.
        if not hasattr(self, '_lastmods'):
            landing_about = _latest(Lan_AboutusModel.objects.all(), 'update_time')
            contact = _latest(ContactModel.objects.all(), 'update_time')
            self._lastmods = {
                'index': _newest(
                    _latest(Product.objects.filter(is_published=True, show_on_landing=True), 'update_time'),
                    _latest(Service.objects.filter(is_published=True, show_on_landing=True), 'update_time'),
                    _latest(Lan_PageBanModel.objects.all(), 'update_time'),
                    landing_about,
                    contact,
                ),
                'homeblog': _latest(Blog.objects.filter(is_published=True), 'updated_at'),
                'web_product': _latest(Product.objects.filter(is_published=True, show_in_catalog=True), 'update_time'),
                'web_dev': _latest(Service.objects.filter(is_published=True, show_in_services=True), 'update_time'),
                'our_module_services': _latest(Service.objects.filter(is_published=True, show_on_module_page=True), 'update_time'),
                'contact': contact,
                'aboutus': _newest(
                    _latest(AboutUSModel.objects.all(), 'update_time'),
                    _latest(AboutVisionModel.objects.all(), 'update_time'),
                ),
                'portfolio': _newest(_latest(PortfolioModel.objects.all(), 'update_time'), landing_about),
            }
        return self._lastmods.get(item)


class ProductSitemap(CanonicalDomainSitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return self._canonical_items(Product.objects.filter(
            show_in_catalog=True,
            is_published=True,
            allow_index=True,
        ).select_related('product_group').order_by('sort_order', 'id'))

    def lastmod(self, item):
        return item.update_time


class ServiceSitemap(CanonicalDomainSitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return self._canonical_items(Service.objects.filter(
            Q(show_in_services=True) | Q(show_on_module_page=True),
            is_published=True,
            allow_index=True,
        ).select_related('service_group').order_by('sort_order', 'id'))

    def lastmod(self, item):
        return item.update_time


class BlogSitemap(CanonicalDomainSitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return self._canonical_items(Blog.objects.filter(
            is_published=True,
            allow_index=True,
        ).order_by('-pub_date', '-id'))

    def lastmod(self, item):
        return item.updated_at


sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'services': ServiceSitemap,
    'blogs': BlogSitemap,
}
