"""Create the small WebP copies of all website images ahead of time.

    python manage.py optimize_images

Without this, each copy is made by the first visitor who needs it (a one-off
delay of about a second for a large PNG). Safe to run more than once: existing
up-to-date copies are skipped. Originals are never changed.
"""
from django.core.management.base import BaseCommand

from web2 import images
from web2.models import Blog, Lan_AboutusModel, Lan_PageBanModel, PortfolioModel, Product, Service

IMAGE_FIELDS = (
    (Lan_PageBanModel, 'img'),
    (Lan_AboutusModel, 'img'),
    (Product, 'img'),
    (Service, 'img'),
    (Blog, 'image'),
    (PortfolioModel, 'img'),
)


class Command(BaseCommand):
    help = 'Create the small WebP copies of the uploaded website images.'

    def handle(self, *args, **options):
        names = set()
        for model, field in IMAGE_FIELDS:
            names.update(name for name in model.objects.exclude(**{field: ''}).values_list(field, flat=True) if name)

        done = failed = 0
        for name in sorted(names):
            if not images.is_optimizable(name):
                continue
            for width in images.WIDTHS:
                try:
                    images.ensure_optimized(name, width)
                    done += 1
                except FileNotFoundError:
                    self.stdout.write(self.style.WARNING(f'  missing  {name}'))
                    failed += 1
                    break
                except Exception as exc:
                    self.stdout.write(self.style.WARNING(f'  failed   {name} ({width}px): {exc}'))
                    failed += 1
        self.stdout.write(self.style.SUCCESS(f'{done} image copies ready, {failed} skipped.'))
