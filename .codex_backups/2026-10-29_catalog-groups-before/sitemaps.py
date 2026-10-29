from urllib.parse import urlparse

from django.contrib.sitemaps import Sitemap
from django.db import OperationalError, ProgrammingError
from django.db.models import Q
from django.urls import reverse

from .models import Blog, Product, Service, SiteSEO


class CanonicalDomainSitemap(Sitemap):
    protocol = 'https'

    def _site_domain(self):
        try:
            site_seo = SiteSEO.objects.first()
        except (OperationalError, ProgrammingError):
            site_seo = None
        return (site_seo.site_domain if site_seo else 'https://www.initiatorsolutions.com').rstrip('/')

    def get_domain(self, site=None):
        parsed = urlparse(self._site_domain())
        return parsed.netloc or parsed.path

    def get_protocol(self, protocol=None):
        parsed = urlparse(self._site_domain())
        return parsed.scheme or 'https'


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
        site_seo = SiteSEO.objects.first()
        return site_seo.updated_at if site_seo else None


class ProductSitemap(CanonicalDomainSitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Product.objects.filter(
            show_in_catalog=True,
            is_published=True,
            allow_index=True,
        ).order_by('sort_order', 'id')

    def lastmod(self, item):
        return item.update_time


class ServiceSitemap(CanonicalDomainSitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Service.objects.filter(
            Q(show_in_services=True) | Q(show_on_module_page=True),
            is_published=True,
            allow_index=True,
        ).order_by('sort_order', 'id')

    def lastmod(self, item):
        return item.update_time


class BlogSitemap(CanonicalDomainSitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Blog.objects.filter(
            is_published=True,
            allow_index=True,
        ).order_by('-pub_date', '-id')

    def lastmod(self, item):
        return item.updated_at


sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'services': ServiceSitemap,
    'blogs': BlogSitemap,
}
