from django.db import migrations
from django.utils.text import slugify


# The fixed choices that Product.product_group / Service.service_group used
# before groups became editable. Slugs are kept so existing URLs do not change.
PRODUCT_GROUPS = [
    ('tally-prime', 'Tally Prime'),
    ('accounting-software', 'All Accounting Software'),
    ('erp-software', 'All ERP Software'),
    ('other', 'Other Products'),
]

SERVICE_GROUPS = [
    ('website-development', 'Website Development'),
    ('web-designing', 'Website Designing'),
    ('web-portal-development', 'Web Portal Development'),
    ('mobile-app-development', 'Mobile App Development'),
    ('tally-customization-integration', 'Tally Customization & Integration'),
    ('tally-vertical-solutions', 'Tally Vertical / Module Services'),
    ('tally-on-cloud', 'Tally On Cloud'),
    ('digital-marketing', 'Digital Marketing'),
    ('graphics-designing', 'Graphics Designing'),
    ('cloud-services', 'Cloud Services'),
    ('other-services', 'Other Services'),
]


def _create_groups(CatalogGroup, group_type, defaults, used_names):
    # used_names: {slug: original stored value} for values found in the data.
    names = dict(defaults)
    slugs = [slug for slug, _ in defaults] + sorted(set(used_names) - set(names))
    groups = {}
    for index, slug in enumerate(slugs, start=1):
        groups[slug], _ = CatalogGroup.objects.get_or_create(
            group_type=group_type,
            slug=slug,
            defaults={
                'name': names.get(slug) or used_names[slug].strip()[:150] or slug.replace('-', ' ').title(),
                'sort_order': index * 10,
            },
        )
    return groups


def _clean_slug(value, fallback):
    # Old rows may hold an empty or non-URL-safe value; such a group slug would
    # break every product/service URL, so map it to a safe slug.
    return slugify(value or '') or fallback


def populate_groups(apps, schema_editor):
    CatalogGroup = apps.get_model('web2', 'CatalogGroup')
    Product = apps.get_model('web2', 'Product')
    Service = apps.get_model('web2', 'Service')

    # queryset.update() keeps update_time (sitemap lastmod) unchanged.
    product_values = list(Product.objects.values_list('product_group', flat=True).distinct())
    product_groups = _create_groups(
        CatalogGroup, 'product', PRODUCT_GROUPS, {_clean_slug(value, 'other'): value for value in product_values},
    )
    for value in product_values:
        Product.objects.filter(product_group=value).update(product_group_ref=product_groups[_clean_slug(value, 'other')])

    service_values = list(Service.objects.values_list('service_group', flat=True).distinct())
    service_groups = _create_groups(
        CatalogGroup, 'service', SERVICE_GROUPS, {_clean_slug(value, 'other-services'): value for value in service_values},
    )
    for value in service_values:
        Service.objects.filter(service_group=value).update(service_group_ref=service_groups[_clean_slug(value, 'other-services')])

    # The Our Modules page used to group module services by their service
    # group, so create matching module groups to keep that page identical.
    module_values = Service.objects.filter(show_on_module_page=True).values_list('service_group', flat=True).distinct()
    for value in module_values:
        slug = _clean_slug(value, 'other-services')
        service_group = service_groups[slug]
        module_group, _ = CatalogGroup.objects.get_or_create(
            group_type='module',
            slug=slug,
            defaults={'name': service_group.name, 'sort_order': service_group.sort_order},
        )
        Service.objects.filter(show_on_module_page=True, service_group=value).update(module_group=module_group)


def restore_group_slugs(apps, schema_editor):
    Product = apps.get_model('web2', 'Product')
    Service = apps.get_model('web2', 'Service')
    for product in Product.objects.select_related('product_group_ref'):
        Product.objects.filter(pk=product.pk).update(product_group=product.product_group_ref.slug)
    for service in Service.objects.select_related('service_group_ref'):
        Service.objects.filter(pk=service.pk).update(service_group=service.service_group_ref.slug)


class Migration(migrations.Migration):

    dependencies = [
        ('web2', '0044_cataloggroup'),
    ]

    operations = [
        migrations.RunPython(populate_groups, restore_group_slugs),
    ]
