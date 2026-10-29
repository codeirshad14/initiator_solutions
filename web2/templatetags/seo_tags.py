import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_H1_OPEN = re.compile(r'<h1(?=[\s>])', re.IGNORECASE)
_H1_CLOSE = re.compile(r'</h1\s*>', re.IGNORECASE)


@register.filter
def phone_digits(value):
    """'+91 88825 95800' -> '918882595800' for tel: and wa.me links.
    A 10-digit Indian number gets the 91 country code."""
    digits = re.sub(r'\D', '', value or '')
    if len(digits) == 11 and digits.startswith('0'):
        digits = digits[1:]
    if len(digits) == 10:
        digits = f'91{digits}'
    return digits


@register.filter
def demote_h1(value):
    """Admin rich text: turn <h1> into <h2 data-rich-h1> so every page keeps a
    single H1 (the page title). Page CSS gives h2[data-rich-h1] the old h1 size.
    Like |safe, the result is rendered as HTML."""
    if not value:
        return value
    return mark_safe(_H1_CLOSE.sub('</h2>', _H1_OPEN.sub('<h2 data-rich-h1', str(value))))
