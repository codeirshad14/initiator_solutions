import html
import uuid

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import Truncator, slugify

# Create your models here.


def plain_text_summary(value, limit=155):
    """Rich text -> clean one-line text for meta descriptions (no tags, &nbsp; or mid-word cuts)."""
    text = ' '.join(html.unescape(strip_tags(value or '')).split())
    return Truncator(text).chars(limit)


# Admin hints shared by the Product, Service and Blog SEO fields.
HELP_META_TITLE = (
    'Blue link text in Google. Aim for 50-60 characters: main keyword first, brand last, '
    'e.g. "Tally Prime Licence & Setup in Noida | INITIATOR SOLUTIONS". Leave blank to use the name.'
)
HELP_META_DESCRIPTION = (
    'Grey text under the link in Google. Aim for 120-155 characters: what it is + benefit + location. '
    'Leave blank to use the answer summary or short description.'
)
HELP_META_KEYWORDS = 'Optional, comma separated. Google ignores this tag; it is only a fallback for internal keywords.'
HELP_FOCUS_KEYWORD = (
    'The one search phrase this page should rank for, e.g. "Tally customization Noida". '
    'Use it in the meta title, the first paragraph and one heading.'
)
HELP_CANONICAL = (
    'Leave blank (recommended). Fill only if the same content lives at another URL that should rank instead; '
    'the page is then left out of sitemap.xml.'
)
HELP_ALLOW_INDEX = 'Untick to hide this page from Google: adds noindex and removes it from sitemap.xml and llms.txt.'
HELP_ANSWER_SUMMARY = (
    'AEO / AI search: 1-2 plain factual sentences (40-60 words) that directly answer "what is this, who is it for, where". '
    'Used as the meta description fallback, in structured data and in llms.txt.'
)
HELP_SORT_ORDER = 'Lower numbers show first.'
HELP_RICH_CONTENT = (
    'Full page content. The page title is already the H1, so use Heading 2 / Heading 3 for sections. '
    'Start with a 2-sentence answer (what, for whom, where), then details, steps, FAQs and links to related pages.'
)
HELP_CARD_IMAGE = (
    'Recommended 1200 x 800 px (3:2), WebP or PNG/JPG, ideally under 200 KB. '
    'The whole image is shown (not cropped), so transparent or white backgrounds look best. Optional.'
)
HELP_IMAGE_ALT = 'Describe the image for Google and screen readers, e.g. "Tally Prime GST invoice screen". Blank uses the name.'


def validate_product_image_size(uploaded_file):
    return None


def validate_product_file_size(uploaded_file):
    return None


#######Product  Model  Details here

class Tally_Prime_Model(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    product_uploads = GenericRelation('ProductUpload', related_query_name='tally_prime_products')
    title   = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/product', default='',blank=True)
    p1      = models.TextField(blank=True, default='',null=True)
    p2      = models.TextField(blank=True, default='',null=True)
    p3      = models.TextField(blank=True, default='',null=True)
    p4      = models.TextField(blank=True, default='',null=True)
    p5      = models.TextField(blank=True, default='',null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


########All Accounting Fetaures Details Here
class All_AccoutingModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    product_uploads = GenericRelation('ProductUpload', related_query_name='accounting_products')
    title   = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/product', default='',blank=True)
    p1      = models.TextField(blank=True, default='',null=True)
    p2      = models.TextField(blank=True, default='',null=True)
    p3      = models.TextField(blank=True, default='',null=True)
    p4      = models.TextField(blank=True, default='',null=True)
    p5      = models.TextField(blank=True, default='',null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


########All All Other Erp  All ************

class All_ERPModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    product_uploads = GenericRelation('ProductUpload', related_query_name='erp_products')
    title   = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/product', default='',blank=True)
    p1      = models.TextField(blank=True, default='',null=True)
    p2      = models.TextField(blank=True, default='',null=True)
    p3      = models.TextField(blank=True, default='',null=True)
    p4      = models.TextField(blank=True, default='',null=True)
    p5      = models.TextField(blank=True, default='',null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class CatalogGroup(models.Model):
    TYPE_PRODUCT = 'product'
    TYPE_SERVICE = 'service'
    TYPE_MODULE = 'module'
    TYPE_CHOICES = [
        (TYPE_PRODUCT, 'Product'),
        (TYPE_SERVICE, 'Service'),
        (TYPE_MODULE, 'Our Modules'),
    ]

    group_type = models.CharField(
        'Group for',
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_PRODUCT,
        help_text='Product groups filter the Products page, Service groups the Services page and Our Modules groups the Our Modules page.'
    )
    name = models.CharField(max_length=150, help_text='Shown as the filter button and badge, e.g. "Tally Prime" or "Website Development".')
    slug = models.SlugField(
        max_length=150,
        blank=True,
        help_text='Used in page URLs. Leave blank to create it from the name. Do not change after items are published (old links would break).'
    )
    sort_order = models.PositiveIntegerField(default=0, help_text='Order of the filter buttons. ' + HELP_SORT_ORDER)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['group_type', 'sort_order', 'name']
        verbose_name = 'Product / Service / Module Group'
        verbose_name_plural = 'Product / Service / Module Groups'
        constraints = [
            models.UniqueConstraint(fields=['group_type', 'slug'], name='unique_catalog_group_slug_per_type'),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)[:140] or 'group'
            slug = base_slug
            counter = 2
            while CatalogGroup.objects.filter(group_type=self.group_type, slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Product(models.Model):
    # Slugs of the default product groups created by migration 0045.
    GROUP_TALLY = 'tally-prime'
    GROUP_ACCOUNTING = 'accounting-software'
    GROUP_ERP = 'erp-software'
    GROUP_OTHER = 'other'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_uploads = GenericRelation('ProductUpload', related_query_name='products')
    product_group = models.ForeignKey(
        CatalogGroup,
        on_delete=models.PROTECT,
        related_name='products',
        limit_choices_to={'group_type': CatalogGroup.TYPE_PRODUCT},
        help_text='Filter group on the Products page and part of the page URL. Create new groups under "Product / Service / Module Groups".'
    )
    title = models.CharField(max_length=200, blank=True, default='', help_text='Optional second title. Used only when Name is blank.')
    name = models.CharField(max_length=200, blank=True, default='', help_text='Product name shown as the page H1 and on cards, e.g. "Tally Prime Silver".')
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, help_text='Internal identifier, filled from the name. The page URL uses the group and ID.')
    img = models.ImageField(
        upload_to='web2/product',
        default='',
        blank=True,
        help_text=HELP_CARD_IMAGE + ' Used on product cards, the detail page and link previews.'
    )
    short_description = models.TextField(
        blank=True,
        default='',
        help_text='1-2 sentences (about 120-160 characters) shown on product cards and the home page. Formatting is removed on cards.'
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text=HELP_RICH_CONTENT
    )
    show_in_catalog = models.BooleanField(default=True, help_text='Show on the Products page and in sitemap.xml.')
    show_on_landing = models.BooleanField(default=False, help_text='Also show in "Our Products" on the home page.')
    is_published = models.BooleanField(default=True, help_text='Untick to take the page offline (returns 404).')
    allow_index = models.BooleanField(default=True, help_text=HELP_ALLOW_INDEX)
    sort_order = models.PositiveIntegerField(default=0, help_text=HELP_SORT_ORDER)
    focus_keyword = models.CharField(max_length=150, blank=True, default='', help_text=HELP_FOCUS_KEYWORD)
    meta_title = models.CharField(max_length=255, blank=True, default='', help_text=HELP_META_TITLE)
    meta_description = models.TextField(blank=True, default='', help_text=HELP_META_DESCRIPTION)
    meta_keywords = models.TextField(blank=True, default='', help_text=HELP_META_KEYWORDS)
    canonical_url = models.URLField(blank=True, default='', help_text=HELP_CANONICAL)
    answer_summary = models.TextField(
        blank=True,
        default='',
        help_text=HELP_ANSWER_SUMMARY
    )
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return str(self.name or self.title)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'group': self.product_group.slug, 'id': self.id})

    def display_title(self):
        return self.name or self.title

    def seo_title(self):
        return self.meta_title or self.display_title()

    def seo_description(self):
        return self.meta_description or self.answer_summary or plain_text_summary(self.short_description or self.description or self.display_title())

    def seo_keywords(self):
        keywords = self.meta_keywords or self.product_group.slug.replace('-', ' ')
        if self.focus_keyword and self.focus_keyword not in keywords:
            keywords = f'{self.focus_keyword}, {keywords}' if keywords else self.focus_keyword
        return keywords

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.display_title())[:220] or 'product'
            slug = base_slug
            counter = 2
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                suffix = f'-{counter}'
                slug = f'{base_slug[:255 - len(suffix)]}{suffix}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Service(models.Model):
    # Slugs of the default service groups created by migration 0045; the old
    # service URLs (web_design, tally_cloud, ...) redirect to these filters.
    GROUP_WEB_DEVELOPMENT = 'website-development'
    GROUP_WEB_DESIGNING = 'web-designing'
    GROUP_WEB_PORTAL = 'web-portal-development'
    GROUP_MOBILE_APP = 'mobile-app-development'
    GROUP_TALLY_CUSTOMIZATION = 'tally-customization-integration'
    GROUP_TALLY_VERTICAL = 'tally-vertical-solutions'
    GROUP_TALLY_CLOUD = 'tally-on-cloud'
    GROUP_DIGITAL_MARKETING = 'digital-marketing'
    GROUP_GRAPHICS = 'graphics-designing'
    GROUP_CLOUD = 'cloud-services'
    GROUP_OTHER = 'other-services'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_group = models.ForeignKey(
        CatalogGroup,
        on_delete=models.PROTECT,
        related_name='services',
        limit_choices_to={'group_type': CatalogGroup.TYPE_SERVICE},
        help_text='Filter group on the Services page and part of the page URL. Create new groups under "Product / Service / Module Groups".'
    )
    module_group = models.ForeignKey(
        CatalogGroup,
        on_delete=models.PROTECT,
        related_name='module_services',
        limit_choices_to={'group_type': CatalogGroup.TYPE_MODULE},
        blank=True,
        null=True,
        help_text='Group shown on the Our Modules page. Required when "Show on module page" is ticked.'
    )
    title = models.CharField(max_length=200, blank=True, default='', help_text='Optional second title. Used only when Name is blank.')
    name = models.CharField(max_length=200, blank=True, default='', help_text='Service name shown as the page H1 and on cards, e.g. "Tally Customization".')
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, help_text='Internal identifier, filled from the name. The page URL uses the group and ID.')
    img = models.ImageField(upload_to='web2/service', default='', blank=True, help_text=HELP_CARD_IMAGE + ' Used on service/module cards, the detail page and link previews.')
    image_alt = models.CharField(max_length=200, blank=True, default='', help_text=HELP_IMAGE_ALT)
    short_description = models.TextField(
        blank=True,
        default='',
        help_text='1-2 sentences (about 120-160 characters) shown on service cards and the home page. Formatting is removed on cards.'
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text=HELP_RICH_CONTENT
    )
    show_in_services = models.BooleanField(default=True, help_text='Show on the Services page.')
    show_on_landing = models.BooleanField(default=False, help_text='Also show in "Our Services" on the home page.')
    show_on_module_page = models.BooleanField(
        default=False,
        help_text='Show on the Our Modules page (also pick a Module group).'
    )
    is_published = models.BooleanField(default=True, help_text='Untick to take the page offline (returns 404).')
    allow_index = models.BooleanField(default=True, help_text=HELP_ALLOW_INDEX)
    sort_order = models.PositiveIntegerField(default=0, help_text=HELP_SORT_ORDER)
    focus_keyword = models.CharField(max_length=150, blank=True, default='', help_text=HELP_FOCUS_KEYWORD)
    meta_title = models.CharField(max_length=255, blank=True, default='', help_text=HELP_META_TITLE)
    meta_description = models.TextField(blank=True, default='', help_text=HELP_META_DESCRIPTION)
    meta_keywords = models.TextField(blank=True, default='', help_text=HELP_META_KEYWORDS)
    canonical_url = models.URLField(blank=True, default='', help_text=HELP_CANONICAL)
    answer_summary = models.TextField(
        blank=True,
        default='',
        help_text=HELP_ANSWER_SUMMARY
    )
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return str(self.name or self.title)

    def clean(self):
        if self.show_on_module_page and not self.module_group_id:
            raise ValidationError({'module_group': 'Select a module group to show this service on the Our Modules page.'})

    def get_absolute_url(self):
        return reverse('service_detail', kwargs={'group': self.service_group.slug, 'id': self.id})

    def display_title(self):
        return self.name or self.title

    def seo_title(self):
        return self.meta_title or self.display_title()

    def seo_description(self):
        return self.meta_description or self.answer_summary or plain_text_summary(self.short_description or self.description or self.display_title())

    def seo_keywords(self):
        keywords = self.meta_keywords or self.service_group.slug.replace('-', ' ')
        if self.focus_keyword and self.focus_keyword not in keywords:
            keywords = f'{self.focus_keyword}, {keywords}' if keywords else self.focus_keyword
        return keywords

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.display_title())[:220] or 'service'
            slug = base_slug
            counter = 2
            while Service.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                suffix = f'-{counter}'
                slug = f'{base_slug[:255 - len(suffix)]}{suffix}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)




##################BLOG MODEL  HERE ##############

class Blog(models.Model):
    title = models.CharField(max_length=255, help_text='Post title, shown as the page H1. Ideally a question or "How to ..." phrase under 60 characters.')
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, help_text='Blog URL: /web2/blog/<slug>/. Lowercase words with hyphens. Do not change after publishing (old links would break).')
    type = models.CharField(max_length=100, help_text='Category shown on cards and used for filtering, e.g. "Tally", "ERP", "Website".')
    pub_date = models.DateTimeField(help_text='Publish date shown on the post and in structured data. Newest posts show first.')
    body = models.TextField(help_text=HELP_RICH_CONTENT + ' Add a dated "Last updated" note when you refresh facts.')
    image = models.ImageField(
        upload_to='web2/blog',
        default='',
        blank=True,
        help_text='Recommended 1600 x 900 px (16:9), WebP or JPG, ideally under 250 KB. Cards crop the edges, so keep the subject in the centre. Optional.'
    )
    alt = models.CharField(max_length=100, blank=True, default='', help_text=HELP_IMAGE_ALT.replace('name', 'post title'))
    author_name = models.CharField(max_length=100, blank=True, default='Initiator Team', help_text='A real person\'s name builds trust (E-E-A-T). "Initiator Team" is marked up as the company.')
    tags = models.CharField(max_length=255, blank=True, default='', help_text='Comma separated, e.g. "Tally, GST, TDL". Shown as clickable tags.')
    focus_keyword = models.CharField(max_length=150, blank=True, default='', help_text=HELP_FOCUS_KEYWORD)
    meta_title = models.CharField(max_length=255, blank=True, default='', help_text=HELP_META_TITLE.replace('Leave blank to use the name.', 'Leave blank to use the post title.'))
    meta_description = models.TextField(blank=True, default='', help_text=HELP_META_DESCRIPTION.replace('answer summary or short description', 'answer summary or the first lines of the post'))
    meta_keywords = models.TextField(blank=True, default='', help_text=HELP_META_KEYWORDS)
    canonical_url = models.URLField(blank=True, default='', help_text=HELP_CANONICAL)
    answer_summary = models.TextField(
        blank=True,
        default='',
        help_text=HELP_ANSWER_SUMMARY
    )
    allow_index = models.BooleanField(default=True, help_text=HELP_ALLOW_INDEX)
    is_published = models.BooleanField(default=True, help_text='Untick to take the post offline (returns 404).')
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title

    def summary(self):
        return strip_tags(self.body)[:150]

    def fullsummary(self):
        return self.body

    def pub_date_pretty(self):
        return self.pub_date.strftime('%b %e %Y')

    def get_absolute_url(self):
        if self.slug:
            return reverse('blog_detail', kwargs={'slug': self.slug})
        return reverse('blog_single', kwargs={'id': self.id})

    def seo_title(self):
        return self.meta_title or self.title

    def seo_description(self):
        return self.meta_description or self.answer_summary or plain_text_summary(self.body)

    def seo_keywords(self):
        keywords = self.meta_keywords or self.tags or self.type
        if self.focus_keyword and self.focus_keyword not in keywords:
            keywords = f'{self.focus_keyword}, {keywords}' if keywords else self.focus_keyword
        return keywords

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title)[:220] or 'blog'
            slug = base_slug
            counter = 2
            while Blog.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                suffix = f'-{counter}'
                slug = f'{base_slug[:255 - len(suffix)]}{suffix}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class SiteSEO(models.Model):
    site_name = models.CharField(max_length=150, default='INITIATOR SOLUTIONS', help_text='Website name used in link previews (og:site_name) and llms.txt.')
    site_domain = models.URLField(
        default='https://www.initiatorsolutions.com',
        help_text='The one main address, with https://www. Used for canonical URLs, sitemap.xml, schema and IndexNow. Must match the live domain exactly.'
    )
    default_title = models.CharField(
        max_length=255,
        default='INITIATOR SOLUTIONS - Software Development & Tally Solutions',
        help_text='Home page title in Google. Aim for 50-60 characters, main keyword first, brand last, '
                  'e.g. "Tally Customization & Software Company Noida | INITIATOR SOLUTIONS".'
    )
    default_description = models.TextField(
        default='Initiator Solutions provides software development, website development, Tally customization, Tally integration, ERP, accounting software, cloud, mobile app and digital marketing services.',
        help_text='Home page description in Google (and fallback for other pages). Aim for 120-155 characters: who you are, what you do, where.'
    )
    default_keywords = models.TextField(
        default='software development company, Tally customization, Tally integration, ERP software, accounting software, website development, mobile app development, digital marketing, Initiator Solutions',
        help_text=HELP_META_KEYWORDS
    )
    google_analytics_id = models.CharField(max_length=50, blank=True, default='', help_text='GA4 Measurement ID, e.g. G-ABC123XYZ. Form, phone and WhatsApp clicks are sent as events automatically.')
    google_tag_manager_id = models.CharField(max_length=50, blank=True, default='', help_text='Optional, e.g. GTM-ABC1234. Use either GA4 here or GA4 inside GTM, not both.')
    microsoft_clarity_id = models.CharField(max_length=50, blank=True, default='', help_text='Optional Microsoft Clarity project ID (heatmaps / recordings).')
    google_site_verification = models.CharField(max_length=255, blank=True, default='', help_text='Only the content="..." value of the google-site-verification meta tag. Not needed if Search Console is verified by DNS.')
    bing_site_verification = models.CharField(max_length=255, blank=True, default='', help_text='Only the content="..." value of the msvalidate.01 meta tag. Not needed if Bing was imported from Search Console.')
    default_og_image = models.CharField(
        max_length=255,
        blank=True,
        default='/static/web2/assets/img/logo.png',
        help_text='Link preview image (WhatsApp, LinkedIn, Facebook) for pages without their own image. '
                  'Recommended 1200 x 630 px JPG/PNG under 300 KB. Enter /static/... path or a full https:// URL. Also used as the logo in schema.'
    )
    organization_name = models.CharField(
        max_length=150,
        default='INITIATOR SOLUTIONS',
        help_text='Exact legal/brand name. Use the identical spelling on the website, Google Business Profile, LinkedIn and directories (entity clarity).'
    )
    business_type = models.CharField(max_length=150, default='SoftwareCompany', help_text='Reference only; structured data always uses Organization + LocalBusiness.')
    founder_name = models.CharField(max_length=150, blank=True, default='', help_text='Optional, real name only. Added to Organization schema (helps Google and AI tools identify the company).')
    founding_year = models.CharField(max_length=4, blank=True, default='', help_text='Optional, e.g. 2016. Added to Organization schema as foundingDate.')
    opening_hours = models.CharField(
        max_length=100,
        blank=True,
        default='Mo-Fr 10:00-18:30',
        help_text='schema.org format, e.g. "Mo-Fr 10:00-18:30" or "Mo-Sa 10:00-19:00". Keep identical to Google Business Profile. Blank to hide.'
    )
    phone = models.CharField(max_length=50, blank=True, default='+91 8882595800', help_text='With country code. Keep identical to the footer and Google Business Profile (NAP).')
    email = models.EmailField(blank=True, default='info@initiatorsolutions.com', help_text='Public contact email (contact page, schema, llms.txt).')
    street_address = models.CharField(max_length=255, blank=True, default='B-7 Ist Floor Noida Sector-2', help_text='Keep identical to the footer and Google Business Profile (NAP).')
    locality = models.CharField(max_length=100, blank=True, default='Noida', help_text='City.')
    region = models.CharField(max_length=100, blank=True, default='Uttar Pradesh', help_text='State.')
    postal_code = models.CharField(max_length=20, blank=True, default='201301', help_text='PIN code.')
    country = models.CharField(max_length=100, blank=True, default='India')
    latitude = models.CharField(max_length=50, blank=True, default='28.572069493566687', help_text='From Google Maps: right-click your office, copy the first number.')
    longitude = models.CharField(max_length=50, blank=True, default='77.33552571460267', help_text='From Google Maps: the second number.')
    google_maps_url = models.URLField(blank=True, default='', help_text='Your Google Business Profile / Maps share link. Added to schema (hasMap and sameAs).')
    service_area = models.CharField(
        max_length=255,
        blank=True,
        default='Noida, Delhi NCR, India, UAE, Dubai',
        help_text='Comma separated places you serve. Used in schema and llms.txt.'
    )
    same_as = models.TextField(
        blank=True,
        default='https://www.facebook.com/irshad.initiator\nhttps://www.instagram.com/initiator_solutions/\nhttps://www.linkedin.com/in/initiator-solutions-222475210/\nhttps://twitter.com/InitiatorSolut1\nhttps://www.youtube.com/@codingpilot96',
        help_text='One official profile URL per line: LinkedIn company page, YouTube, Facebook, Instagram, X, Justdial, Clutch, etc. '
                  'Tells Google and AI tools these profiles are the same business.'
    )
    ai_answer_summary = models.TextField(
        blank=True,
        default='INITIATOR SOLUTIONS is a software development and business software solutions company serving Tally customization, ERP, accounting software, website development, mobile app, cloud and digital marketing needs.',
        help_text='GEO / AI search: 2-3 factual sentences, e.g. "INITIATOR SOLUTIONS is a Noida-based software company that provides ...". '
                  'Used as the Organization schema description and the llms.txt summary. Facts and numbers, no adjectives.'
    )
    robots_allow = models.BooleanField(default=True, help_text='Keep ticked on the live site. Unticking blocks ALL search engines and AI tools (only for a staging copy).')
    llms_summary = models.TextField(
        blank=True,
        default='Use this website to understand INITIATOR SOLUTIONS services, products, blog knowledge, contact details, local business information and software solution expertise.',
        help_text='Extra note for AI agents shown at the top of /llms.txt.'
    )
    indexnow_enabled = models.BooleanField(
        default=False,
        help_text='Tell Bing / Copilot (IndexNow) instantly when a published product, service or blog post is saved. '
                  'Enable only on the live site; a key is created automatically.'
    )
    indexnow_key = models.CharField(max_length=64, blank=True, default='', help_text='Created automatically. Served at /<key>.txt for IndexNow verification.')
    indexnow_last_status = models.CharField(max_length=255, blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site SEO Setting'
        verbose_name_plural = 'Site SEO Settings'

    def __str__(self):
        return self.site_name

    def same_as_links(self):
        return [line.strip() for line in self.same_as.splitlines() if line.strip()]

    def save(self, *args, **kwargs):
        if self.indexnow_enabled and not self.indexnow_key:
            self.indexnow_key = uuid.uuid4().hex
        super().save(*args, **kwargs)


class ProductUpload(models.Model):
    MAX_FILES_PER_PRODUCT = 100

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')
    title = models.CharField(max_length=200, blank=True, default='')
    file = models.FileField(
        upload_to='web2/product_files',
        help_text='File attached to an old (legacy) product record. These files are not shown on the website at the moment.'
    )
    alt_text = models.CharField(max_length=200, blank=True, default='', help_text=HELP_IMAGE_ALT)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Product Upload'
        verbose_name_plural = 'Product Uploads'

    def __str__(self):
        return self.title or self.file.name

    def clean(self):
        if not self.content_type_id or not self.object_id:
            return
        upload_count = ProductUpload.objects.filter(
            content_type=self.content_type,
            object_id=self.object_id,
        ).exclude(pk=self.pk).count()
        if upload_count >= self.MAX_FILES_PER_PRODUCT:
            raise ValidationError('Only 100 files are allowed for one product.')

    def is_image(self):
        file_name = (self.file.name or '').lower()
        return file_name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'))

##################END BLOG MODEL  HERE ##########

####### CONTACT

class ContactModel(models.Model):

    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    iconcode = models.CharField(max_length=200, blank=True, default='', help_text='Bootstrap icon class, e.g. "bi bi-geo-alt" (address), "bi bi-telephone" (phone), "bi bi-clock" (hours).')
    title    = models.CharField(max_length=200, blank=True, default='', help_text='Box heading on the Contact page and home page, e.g. "Address".')
    p1       = models.CharField(max_length=200, blank=True, default='', help_text='Line 1. Keep address and phone identical to the footer and Google Business Profile (NAP).')
    p2       = models.CharField(max_length=200, blank=True, default='', help_text='Line 2 (optional).')
    p3       = models.CharField(max_length=200, blank=True, default='', help_text='Line 3 (optional).')
    type     = models.CharField(max_length=200, blank=True, default='', help_text='Internal note only; not shown on the website.')

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ContactIntegrationSettings(models.Model):
    provider_name = models.CharField(
        max_length=120,
        default='Zoho CRM / Webhook',
        help_text='Label shown in admin, for example Zoho CRM, Zoho Flow, Zapier or custom CRM.'
    )
    is_enabled = models.BooleanField(default=False)
    endpoint_url = models.URLField(
        blank=True,
        default='',
        help_text='CRM API endpoint or webhook URL that receives enquiry JSON.'
    )
    api_key = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text='API key, bearer token, Zoho access token or webhook secret.'
    )
    auth_header_name = models.CharField(
        max_length=100,
        default='Authorization',
        help_text='Use Authorization for bearer/Zoho tokens, or X-API-Key for simple API-key endpoints.'
    )
    auth_token_prefix = models.CharField(
        max_length=80,
        blank=True,
        default='Bearer',
        help_text='Examples: Bearer, Zoho-oauthtoken, Token. Leave blank when the endpoint wants only the key.'
    )
    extra_headers = models.TextField(
        blank=True,
        default='',
        help_text='Optional JSON object, for example {"X-Source":"Website"}.'
    )
    timeout_seconds = models.PositiveIntegerField(default=10)
    last_status = models.CharField(max_length=255, blank=True, default='')
    last_response = models.TextField(blank=True, default='')
    last_sent_at = models.DateTimeField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact CRM/API Integration'
        verbose_name_plural = 'Contact CRM/API Integration'

    def __str__(self):
        return self.provider_name

#############################################service model  for website
class WebDevModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    title   = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/service', default='',blank=True)
    p1      = models.TextField(blank=True, default='',null=True)
    p2      = models.TextField(blank=True, default='',null=True)
    p3      = models.TextField(blank=True, default='',null=True)
    p4      = models.TextField(blank=True, default='',null=True)
    p5      = models.TextField(blank=True, default='',null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.name)

####### web portal development
class Web_DesignModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    title   = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/service', default='',blank=True)
    p1      = models.TextField(blank=True, default='',null=True)
    p2      = models.TextField(blank=True, default='',null=True)
    p3      = models.TextField(blank=True, default='',null=True)
    p4      = models.TextField(blank=True, default='',null=True)
    p5      = models.TextField(blank=True, default='',null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.name)

############

####### web Portal  Develpment

class Web_Portal_Dev(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    title   = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/service', default='',blank=True)
    p1      = models.TextField(blank=True, default='',null=True)
    p2      = models.TextField(blank=True, default='',null=True)
    p3      = models.TextField(blank=True, default='',null=True)
    p4      = models.TextField(blank=True, default='',null=True)
    p5      = models.TextField(blank=True, default='',null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.name)

####### MObile APP Development

class MobileAppModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    title   = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/service', default='',blank=True)
    p1      = models.TextField(blank=True, default='',null=True)
    p2      = models.TextField(blank=True, default='',null=True)
    p3      = models.TextField(blank=True, default='',null=True)
    p4      = models.TextField(blank=True, default='',null=True)
    p5      = models.TextField(blank=True, default='',null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.name)


####### Tally  Customization & Integration

class Tally_Customization(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    title   = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/service', default='',blank=True)
    p1      = models.TextField(blank=True, default='',null=True)
    p2      = models.TextField(blank=True, default='',null=True)
    p3      = models.TextField(blank=True, default='',null=True)
    p4      = models.TextField(blank=True, default='',null=True)
    p5      = models.TextField(blank=True, default='',null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.name)

############ All  Vertical  solutions Details Here

class Tally_VerticalModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    url    = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/service', default='',blank=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.name)

#######  Tally On  Cloud Model Here
class Tally_CloudModel(models.Model):
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    title   = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/service', default='',blank=True)
    p1      = models.TextField(blank=True, default='',null=True)
    p2      = models.TextField(blank=True, default='',null=True)
    p3      = models.TextField(blank=True, default='',null=True)
    p4      = models.TextField(blank=True, default='',null=True)
    p5      = models.TextField(blank=True, default='',null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.name)

#######  Digital Marketing
class Digital_Mkt_Model(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    title   = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/service', default='',blank=True)
    p1      = models.TextField(blank=True, default='',null=True)
    p2      = models.TextField(blank=True, default='',null=True)
    p3      = models.TextField(blank=True, default='',null=True)
    p4      = models.TextField(blank=True, default='',null=True)
    p5      = models.TextField(blank=True, default='',null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.name)

#######  Graphics Design Details Here
class Graphics_Model(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    title   = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/service', default='',blank=True)
    p1      = models.TextField(blank=True, default='',null=True)
    p2      = models.TextField(blank=True, default='',null=True)
    p3      = models.TextField(blank=True, default='',null=True)
    p4      = models.TextField(blank=True, default='',null=True)
    p5      = models.TextField(blank=True, default='',null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.name)



#######  Cloud Desing Details
class CloudModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    title   = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/service', default='',blank=True)
    p1      = models.TextField(blank=True, default='',null=True)
    p2      = models.TextField(blank=True, default='',null=True)
    p3      = models.TextField(blank=True, default='',null=True)
    p4      = models.TextField(blank=True, default='',null=True)
    p5      = models.TextField(blank=True, default='',null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.name)



################ Web design  Model  Details ********* *************
"""
class WebDesignModel_Title(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, default='')
    para = models.CharField(max_length=200, blank=True, default='')
    type = models.CharField(max_length=200, blank=True, default='')

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.title)


class WebDesignModel(models.Model):
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    title   = models.ForeignKey(ServiceModel_Title, on_delete=models.CASCADE,related_name='weddesignmodel')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/service', default='',blank=True)
    p1      = models.CharField(max_length=255, blank=True, default='')
    p2      = models.CharField(max_length=255, blank=True, default='')
    p3      = models.CharField(max_length=255, blank=True, default='')
    p4      = models.CharField(max_length=255, blank=True, default='')
    p5      = models.CharField(max_length=255, blank=True, default='')

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

"""

####### ABOUT US model one 1
"""
class AboutUSModel_Title(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, default='')
    para = models.CharField(max_length=200, blank=True, default='')
    type = models.CharField(max_length=200, blank=True, default='')

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.title)

"""
#### Our  News Later

class OurNewsLetter(models.Model):

  #  user    = models.ForeignKey(User, on_delete=models.CASCADE)
    title   = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='', help_text='Subscriber email from the footer newsletter form.')

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.name)




HELP_ABOUT_TEXT = (
    'Paragraph on the Who We Are page. The page H1 already exists, so use Heading 2 / Heading 3. '
    'Good for SEO and AI tools: founder name, year founded, city, services, number of clients (real facts only).'
)


class AboutUSModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    p1      = models.TextField(blank=True, default='', null=True, help_text=HELP_ABOUT_TEXT)
    p2      = models.TextField(blank=True, default='', null=True, help_text='Optional second paragraph.')
    p3      = models.TextField(blank=True, default='', null=True, help_text='Optional third paragraph.')

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
     return str(self.p1)

####### ABOUT US model two Vision
"""
class AboutVisionModel_Title(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True, default='')
    para = models.CharField(max_length=200, blank=True, default='')
    type = models.CharField(max_length=200, blank=True, default='')

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)

"""
class AboutVisionModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    p1      = models.TextField(blank=True, default='', null=True, help_text='"Our Vision" paragraph on the Who We Are page. Use Heading 2 / Heading 3 for sub-headings.')
    p2      = models.TextField(blank=True, default='', null=True, help_text='Optional second paragraph.')
    p3      = models.TextField(blank=True, default='', null=True, help_text='Optional third paragraph.')

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.p1)

####################POrtfolio  Details Here *************************************************************************************

class PortfolioModel(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=200, blank=True, default='',
        help_text='Project name, also used as image alt text. These names get a ready-made case description: '
                  '"Tally Invoice Customization", "E-Commerce Tally Integration", "Garments Module Software", '
                  '"Auto Backup For Tally", "Barcode And Label Printing", "Approval System Module".'
    )
    img = models.ImageField(
        upload_to='web2/portfolio', default='', blank=True,
        help_text='Recommended 1400 x 1000 px (7:5), WebP or JPG under 250 KB. Grid cards crop the edges, so keep the subject in the centre.'
    )

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


##########  Landing Page Details Here *************************

class Lan_PageBanModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    Slogen  = models.CharField(max_length=200, blank=True, default='', help_text='Admin label only. The home page heading is fixed in the page design.')
    Slogen2 = models.CharField(max_length=200, blank=True, default='', help_text='Admin label only (not shown on the website).')
    imagalt = models.CharField(max_length=200, blank=True, default='', help_text='Describe the banner image, e.g. "Tally and ERP software dashboard illustration".')
    img     = models.ImageField(
        upload_to='web2/landingpage', default='', blank=True,
        help_text='Home page hero image (right side), also the Portfolio banner. Recommended 1400 x 1000 px, transparent PNG or WebP under 250 KB. '
                  'This is the first image visitors see, so keep it light for fast loading.'
    )

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.Slogen)


########## Landing Page  About Us Details Here *************************

class Lan_AboutusModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    text1  = models.TextField(blank=True, default='', help_text='Heading of the "Who We Are" section on the home page (one sentence).')
    text2 = models.TextField(blank=True, default='', help_text='Paragraph under it. Start with who you are, where, and what you do, e.g. "INITIATOR SOLUTIONS is a Noida-based ...".')
    imagalt = models.CharField(max_length=200, blank=True, default='', help_text='Describe the image for Google and screen readers.')
    img = models.ImageField(
        upload_to='web2/landingpage', default='', blank=True,
        help_text='Home page "Who We Are" image. Recommended 1200 x 900 px (4:3), transparent PNG or WebP under 200 KB. Shown whole (not cropped).'
    )
    client = models.CharField(max_length=200, blank=True, default='', help_text='Numbers only, e.g. 150. Shown as the animated "Happy Clients" counter (also on Portfolio).')
    project = models.CharField(max_length=200, blank=True, default='', help_text='Numbers only. "Projects" counter.')
    emp  = models.CharField(max_length=200, blank=True, default='', help_text='Numbers only. "Hard Workers" counter.')
    hrs  = models.CharField(max_length=200, blank=True, default='', help_text='Numbers only. "Hours Of Support" counter.')


    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.text1)

###### Landing Product  Name
########## Landing Page  Product Details Here *************************

class Lan_ProductModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    product_uploads = GenericRelation('ProductUpload', related_query_name='landing_products')
    title   = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/landingpage', default='',blank=True)
    p1      = models.TextField(blank=True, default='',null=True)
    p2      = models.TextField(blank=True, default='',null=True)
    p3      = models.TextField(blank=True, default='',null=True)
    p4      = models.TextField(blank=True, default='',null=True)
    p5      = models.TextField(blank=True, default='',null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.name)

########## Landing Page  Services Details Here *************************

class Lan_ServicesModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    title   = models.CharField(max_length=200, blank=True, default='')
    name    = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/landingpage', default='',blank=True)
    p1      = models.TextField(blank=True, default='',null=True)
    p2      = models.TextField(blank=True, default='',null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.name)


