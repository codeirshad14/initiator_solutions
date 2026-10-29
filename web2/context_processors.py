import json

from django.db import OperationalError, ProgrammingError
from django.templatetags.static import static

from .models import SiteSEO


def _strip_empty(value):
    if isinstance(value, dict):
        return {
            key: cleaned
            for key, item in value.items()
            if (cleaned := _strip_empty(item)) not in ('', None, [], {})
        }
    if isinstance(value, list):
        return [
            cleaned
            for item in value
            if (cleaned := _strip_empty(item)) not in ('', None, [], {})
        ]
    return value


def schema_json(data):
    # Escape "<" so admin-entered text can never close the surrounding <script> tag.
    return json.dumps(_strip_empty(data)).replace('<', '\\u003c')


def _get_site_seo():
    try:
        return SiteSEO.objects.first() or SiteSEO()
    except (OperationalError, ProgrammingError):
        return SiteSEO()


def _absolute_url(request, base_url, value):
    if not value:
        return ''
    if value.startswith(('http://', 'https://')):
        return value
    if value.startswith('/'):
        return f'{base_url}{value}'
    return request.build_absolute_uri(static(value))


def seo_context(request):
    site_seo = _get_site_seo()
    base_url = (site_seo.site_domain or request.build_absolute_uri('/')).rstrip('/')
    current_url = f'{base_url}{request.path}'
    logo_url = _absolute_url(request, base_url, site_seo.default_og_image)
    same_as = site_seo.same_as_links()
    if site_seo.google_maps_url and site_seo.google_maps_url not in same_as:
        same_as.append(site_seo.google_maps_url)
    service_area = [area.strip() for area in site_seo.service_area.split(',') if area.strip()]

    # One business entity (Organization + LocalBusiness) that every page,
    # service and article references by @id, so search engines and AI tools
    # see a single, unambiguous INITIATOR SOLUTIONS.
    organization_schema = {
        '@context': 'https://schema.org',
        '@type': ['Organization', 'LocalBusiness'],
        '@id': f'{base_url}/#organization',
        'name': site_seo.organization_name,
        'url': f'{base_url}/',
        'logo': logo_url,
        'image': logo_url,
        'description': site_seo.ai_answer_summary,
        'email': site_seo.email,
        'telephone': site_seo.phone,
        'foundingDate': site_seo.founding_year,
        'founder': {'@type': 'Person', 'name': site_seo.founder_name} if site_seo.founder_name else '',
        'address': {
            '@type': 'PostalAddress',
            'streetAddress': site_seo.street_address,
            'addressLocality': site_seo.locality,
            'addressRegion': site_seo.region,
            'postalCode': site_seo.postal_code,
            'addressCountry': site_seo.country,
        },
        'geo': {
            '@type': 'GeoCoordinates',
            'latitude': site_seo.latitude,
            'longitude': site_seo.longitude,
        },
        'hasMap': site_seo.google_maps_url,
        'openingHours': site_seo.opening_hours,
        'areaServed': service_area,
        'contactPoint': {
            '@type': 'ContactPoint',
            'telephone': site_seo.phone,
            'email': site_seo.email,
            'contactType': 'customer support',
            'areaServed': service_area,
            'availableLanguage': ['English', 'Hindi'],
        },
        'sameAs': same_as,
    }

    website_schema = {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': f'{base_url}/#website',
        'name': site_seo.site_name,
        'url': f'{base_url}/',
        'inLanguage': 'en-IN',
        'publisher': {'@id': f'{base_url}/#organization'},
    }

    return {
        'site_seo': site_seo,
        'seo_base_url': base_url,
        'seo_current_url': current_url,
        'seo_default_image': logo_url,
        'organization_schema_json': schema_json(organization_schema),
        'website_schema_json': schema_json(website_schema),
    }
