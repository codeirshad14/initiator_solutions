from django import template

from web2.images import optimized_url

register = template.Library()


@register.filter
def image_url(image, width=1200):
    """{{ item.img|image_url:800 }} -> URL of a smaller WebP copy (original URL as fallback)."""
    return optimized_url(image, int(width))
