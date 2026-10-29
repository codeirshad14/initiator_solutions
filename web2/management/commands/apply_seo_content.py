"""Apply the SEO content from web2/seo_content.py to the database.

    python manage.py apply_seo_content --dry-run      # show changes, save nothing
    python manage.py apply_seo_content                # apply
    python manage.py apply_seo_content --overwrite-content

Safe to run more than once. SEO fields (name, meta title/description, focus
keyword) always follow seo_content.py. Card text, page content and answer
summary are only filled when empty or very short (under 400 characters), so
real content written in admin is kept unless --overwrite-content is given.
An existing page keeps its group, so its URL never changes.
"""
import re

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from web2 import seo_content
from web2.models import CatalogGroup, Product, Service, SiteSEO, plain_text_summary

THIN_CONTENT_CHARS = 400
SEO_FIELDS = ('name', 'meta_title', 'meta_description', 'focus_keyword')
CONTENT_FIELDS = ('answer_summary', 'short_description', 'description')


def _is_thin(value):
    return len(plain_text_summary(value, limit=10000)) < THIN_CONTENT_CHARS


class Command(BaseCommand):
    help = 'Apply the Initiator Solutions SEO content (site settings, groups and service pages).'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would change without saving.')
        parser.add_argument('--overwrite-content', action='store_true', help='Also replace existing long page content.')

    def handle(self, *args, **options):
        self.overwrite = options['overwrite_content']
        self.user = User.objects.filter(is_superuser=True).order_by('id').first() or User.objects.order_by('id').first()
        if self.user is None:
            raise CommandError('Create an admin user first (python manage.py createsuperuser).')

        with transaction.atomic():
            self.apply_site_seo()
            groups = self.apply_groups()
            pages = {page['key']: self.apply_page(page, groups) for page in seo_content.PAGES}
            self.apply_links(pages)
            if options['dry_run']:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING('Dry run: nothing was saved.'))
            else:
                self.stdout.write(self.style.SUCCESS('SEO content applied.'))

    def log(self, action, label):
        self.stdout.write(f'  {action:<9} {label}')

    def apply_site_seo(self):
        site_seo = SiteSEO.objects.first() or SiteSEO()
        changed = [field for field, value in seo_content.SITE_SEO.items() if getattr(site_seo, field) != value]
        for field in changed:
            setattr(site_seo, field, seo_content.SITE_SEO[field])
        if changed or not site_seo.pk:
            site_seo.save()
        self.log('updated' if changed else 'ok', f'Site SEO settings {changed or ""}')

    def apply_groups(self):
        groups = {}
        for slug, name, sort_order in seo_content.SERVICE_GROUPS:
            group, created = CatalogGroup.objects.get_or_create(
                group_type=CatalogGroup.TYPE_SERVICE,
                slug=slug,
                defaults={'name': name, 'sort_order': sort_order},
            )
            groups[('service', slug)] = group
            self.log('created' if created else 'ok', f'Service group "{group.name}"')
        return groups

    def _find_existing(self, model, page):
        for slug in [page['key']] + page['match_slugs']:
            item = model.objects.filter(slug=slug).first()
            if item:
                return item
        for name in [page['name']] + page['match_names']:
            item = model.objects.filter(name__iexact=name).order_by('id').first()
            if item:
                return item
        return None

    def _group_for(self, page, groups):
        if page['kind'] == 'product':
            group, _ = CatalogGroup.objects.get_or_create(
                group_type=CatalogGroup.TYPE_PRODUCT, slug=page['group'],
                defaults={'name': page['group'].replace('-', ' ').title()},
            )
            return group
        return groups[('service', page['group'])]

    def apply_page(self, page, groups):
        model = Product if page['kind'] == 'product' else Service
        group_field = 'product_group' if model is Product else 'service_group'
        item = self._find_existing(model, page)
        created = item is None
        if created:
            item = model(user=self.user, is_published=True, allow_index=True)
            setattr(item, group_field, self._group_for(page, groups))
            if model is Product:
                item.show_in_catalog = True
            else:
                item.show_in_services = True

        changed = []
        for field in SEO_FIELDS:
            if getattr(item, field) != page[field]:
                setattr(item, field, page[field])
                changed.append(field)
        for field in CONTENT_FIELDS:
            if self.overwrite or _is_thin(getattr(item, field)):
                # Descriptions get their {link:...} placeholders filled in apply_links().
                if getattr(item, field) != page[field]:
                    setattr(item, field, page[field])
                    changed.append(field)
        key_is_free = not model.objects.filter(slug=page['key']).exclude(pk=item.pk).exists()
        if item.slug != page['key'] and key_is_free:
            item.slug = page['key']
            changed.append('slug')
        # Otherwise keep the slug; a blank one is generated from the name on save().
        if not item.img:
            sibling = model.objects.filter(**{group_field: getattr(item, group_field)}).exclude(img='').exclude(pk=item.pk).first()
            if sibling:
                item.img = sibling.img.name
                changed.append('img')

        if created or changed:
            item.save()
        self.log('created' if created else ('updated' if changed else 'ok'), f'{page["kind"].title()} "{item.name}" {changed if not created else ""}')
        return item

    def apply_links(self, pages):
        for item in pages.values():
            description = re.sub(
                r'\{link:([a-z0-9-]+)\}',
                lambda match: pages[match.group(1)].get_absolute_url() if match.group(1) in pages else '#',
                item.description,
            )
            if description != item.description:
                type(item).objects.filter(pk=item.pk).update(description=description)
                item.description = description
