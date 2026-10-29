"""Smaller WebP copies of uploaded images, so pages do not download multi-MB originals.

Admin uploads are often full-size PNG exports (2-7 MB each), which made the home
page hero and the product / service cards slow. Templates use
{{ item.img|image_url:800 }}; views.optimized_image makes the copy on the first
request (or `python manage.py optimize_images` makes them all at deploy time) and
caches it under MEDIA_ROOT/_optimized/. Originals are never changed, and any
image that cannot be converted is served as the original file.
"""
import os
from uuid import uuid4

from django.conf import settings
from django.urls import reverse
from django.utils._os import safe_join
from PIL import Image, ImageOps

# Allowed copy widths (px). 400: sidebar thumbnails, 800: cards, 1200: hero / detail images.
WIDTHS = (400, 800, 1200)
OPTIMIZED_DIR = '_optimized'
RASTER_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff')
WEBP_QUALITY = 82


def is_optimizable(name):
    return bool(name) and name.lower().endswith(RASTER_EXTENSIONS) and not name.startswith(f'{OPTIMIZED_DIR}/')


def optimized_url(image, width):
    """URL of the WebP copy of an ImageField file, or its original URL if it cannot have one."""
    name = getattr(image, 'name', '') or ''
    if not name:
        return ''
    if width not in WIDTHS or not is_optimizable(name):
        return image.url
    return reverse('optimized_image', kwargs={'width': width, 'name': name})


def optimized_path(name, width):
    return safe_join(settings.MEDIA_ROOT, OPTIMIZED_DIR, str(width), f'{name}.webp')


def ensure_optimized(name, width):
    """Return the file path of the WebP copy, creating it when missing or older than the original.

    Raises FileNotFoundError when the original does not exist and
    SuspiciousFileOperation when the name points outside MEDIA_ROOT.
    """
    source = safe_join(settings.MEDIA_ROOT, name)
    target = optimized_path(name, width)
    if os.path.exists(target) and os.path.getmtime(target) >= os.path.getmtime(source):
        return target

    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        has_alpha = image.mode in ('RGBA', 'LA', 'PA') or (image.mode == 'P' and 'transparency' in image.info)
        image = image.convert('RGBA' if has_alpha else 'RGB')
        # Never upscale; keep the aspect ratio.
        image.thumbnail((width, width * 20), Image.LANCZOS, reducing_gap=3.0)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        # Write to a temporary name first so a visitor never gets a half-written file.
        temp_path = f'{target}.{uuid4().hex}.tmp'
        try:
            image.save(temp_path, 'WEBP', quality=WEBP_QUALITY, method=4)
            os.replace(temp_path, target)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    return target
