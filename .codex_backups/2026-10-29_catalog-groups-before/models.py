from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import slugify

# Create your models here.


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


class Product(models.Model):
    GROUP_TALLY = 'tally-prime'
    GROUP_ACCOUNTING = 'accounting-software'
    GROUP_ERP = 'erp-software'
    GROUP_OTHER = 'other'
    GROUP_CHOICES = [
        (GROUP_TALLY, 'Tally Prime'),
        (GROUP_ACCOUNTING, 'All Accounting Software'),
        (GROUP_ERP, 'All ERP Software'),
        (GROUP_OTHER, 'Other Products'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_uploads = GenericRelation('ProductUpload', related_query_name='products')
    product_group = models.CharField(max_length=50, choices=GROUP_CHOICES, default=GROUP_TALLY)
    title = models.CharField(max_length=200, blank=True, default='')
    name = models.CharField(max_length=200, blank=True, default='')
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    img = models.ImageField(
        upload_to='web2/product',
        default='',
        blank=True,
        help_text='Upload one product image. No image size limit is enforced by Django.'
    )
    short_description = models.TextField(
        blank=True,
        default='',
        help_text='Short plain summary used on product cards and landing page.'
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text='Full rich text product details for the product detail page.'
    )
    show_in_catalog = models.BooleanField(default=True)
    show_on_landing = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    allow_index = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    focus_keyword = models.CharField(max_length=150, blank=True, default='')
    meta_title = models.CharField(max_length=255, blank=True, default='')
    meta_description = models.TextField(blank=True, default='')
    meta_keywords = models.TextField(blank=True, default='')
    canonical_url = models.URLField(blank=True, default='')
    answer_summary = models.TextField(
        blank=True,
        default='',
        help_text='Short answer for AEO/GEO/AI search summaries.'
    )
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return str(self.name or self.title)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'group': self.product_group, 'id': self.id})

    def display_title(self):
        return self.name or self.title

    def seo_title(self):
        return self.meta_title or self.display_title()

    def seo_description(self):
        return self.meta_description or self.answer_summary or strip_tags(self.short_description or self.description or self.display_title())[:160]

    def seo_keywords(self):
        keywords = self.meta_keywords or self.product_group.replace('-', ' ')
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
    GROUP_CHOICES = [
        (GROUP_WEB_DEVELOPMENT, 'Website Development'),
        (GROUP_WEB_DESIGNING, 'Website Designing'),
        (GROUP_WEB_PORTAL, 'Web Portal Development'),
        (GROUP_MOBILE_APP, 'Mobile App Development'),
        (GROUP_TALLY_CUSTOMIZATION, 'Tally Customization & Integration'),
        (GROUP_TALLY_VERTICAL, 'Tally Vertical / Module Services'),
        (GROUP_TALLY_CLOUD, 'Tally On Cloud'),
        (GROUP_DIGITAL_MARKETING, 'Digital Marketing'),
        (GROUP_GRAPHICS, 'Graphics Designing'),
        (GROUP_CLOUD, 'Cloud Services'),
        (GROUP_OTHER, 'Other Services'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_group = models.CharField(max_length=60, choices=GROUP_CHOICES, default=GROUP_WEB_DEVELOPMENT)
    title = models.CharField(max_length=200, blank=True, default='')
    name = models.CharField(max_length=200, blank=True, default='')
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    img = models.ImageField(upload_to='web2/service', default='', blank=True)
    image_alt = models.CharField(max_length=200, blank=True, default='')
    short_description = models.TextField(
        blank=True,
        default='',
        help_text='Short plain summary used on service cards and landing page.'
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text='Full rich text service details for the service detail page.'
    )
    show_in_services = models.BooleanField(default=True)
    show_on_landing = models.BooleanField(default=False)
    show_on_module_page = models.BooleanField(
        default=False,
        help_text='Enable this for special services that should appear on Our Modules page.'
    )
    is_published = models.BooleanField(default=True)
    allow_index = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    focus_keyword = models.CharField(max_length=150, blank=True, default='')
    meta_title = models.CharField(max_length=255, blank=True, default='')
    meta_description = models.TextField(blank=True, default='')
    meta_keywords = models.TextField(blank=True, default='')
    canonical_url = models.URLField(blank=True, default='')
    answer_summary = models.TextField(
        blank=True,
        default='',
        help_text='Short answer for AEO/GEO/AI search summaries.'
    )
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return str(self.name or self.title)

    def get_absolute_url(self):
        return reverse('service_detail', kwargs={'group': self.service_group, 'id': self.id})

    def display_title(self):
        return self.name or self.title

    def seo_title(self):
        return self.meta_title or self.display_title()

    def seo_description(self):
        return self.meta_description or self.answer_summary or strip_tags(self.short_description or self.description or self.display_title())[:160]

    def seo_keywords(self):
        keywords = self.meta_keywords or self.service_group.replace('-', ' ')
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
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    type = models.CharField(max_length=100)
    pub_date = models.DateTimeField()
    body = models.TextField()
    image = models.ImageField(
        upload_to='web2/blog',
        default='',
        blank=True,
        help_text='Upload a blog image. No image size limit is enforced by Django.'
    )
    alt = models.CharField(max_length=100, blank=True, default='')
    author_name = models.CharField(max_length=100, blank=True, default='Initiator Team')
    tags = models.CharField(max_length=255, blank=True, default='')
    focus_keyword = models.CharField(max_length=150, blank=True, default='')
    meta_title = models.CharField(max_length=255, blank=True, default='')
    meta_description = models.TextField(blank=True, default='')
    meta_keywords = models.TextField(blank=True, default='')
    canonical_url = models.URLField(blank=True, default='')
    answer_summary = models.TextField(
        blank=True,
        default='',
        help_text='Short answer for AEO/GEO/AI search summaries.'
    )
    allow_index = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
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
        return self.meta_description or self.answer_summary or strip_tags(self.body)[:160]

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
    site_name = models.CharField(max_length=150, default='INITIATOR SOLUTIONS')
    site_domain = models.URLField(default='https://www.initiatorsolutions.com')
    default_title = models.CharField(
        max_length=255,
        default='INITIATOR SOLUTIONS - Software Development & Tally Solutions'
    )
    default_description = models.TextField(
        default='Initiator Solutions provides software development, website development, Tally customization, Tally integration, ERP, accounting software, cloud, mobile app and digital marketing services.'
    )
    default_keywords = models.TextField(
        default='software development company, Tally customization, Tally integration, ERP software, accounting software, website development, mobile app development, digital marketing, Initiator Solutions'
    )
    google_analytics_id = models.CharField(max_length=50, blank=True, default='')
    google_tag_manager_id = models.CharField(max_length=50, blank=True, default='')
    microsoft_clarity_id = models.CharField(max_length=50, blank=True, default='')
    google_site_verification = models.CharField(max_length=255, blank=True, default='')
    bing_site_verification = models.CharField(max_length=255, blank=True, default='')
    default_og_image = models.CharField(
        max_length=255,
        blank=True,
        default='/static/web2/assets/img/logo.png'
    )
    organization_name = models.CharField(max_length=150, default='INITIATOR SOLUTIONS')
    business_type = models.CharField(max_length=150, default='SoftwareCompany')
    phone = models.CharField(max_length=50, blank=True, default='+91 8882595800')
    email = models.EmailField(blank=True, default='info@initiatorsolutions.com')
    street_address = models.CharField(max_length=255, blank=True, default='B-7 Ist Floor Noida Sector-2')
    locality = models.CharField(max_length=100, blank=True, default='Noida')
    region = models.CharField(max_length=100, blank=True, default='Uttar Pradesh')
    postal_code = models.CharField(max_length=20, blank=True, default='201301')
    country = models.CharField(max_length=100, blank=True, default='India')
    latitude = models.CharField(max_length=50, blank=True, default='28.572069493566687')
    longitude = models.CharField(max_length=50, blank=True, default='77.33552571460267')
    google_maps_url = models.URLField(blank=True, default='')
    service_area = models.CharField(
        max_length=255,
        blank=True,
        default='Noida, Delhi NCR, India, UAE, Dubai'
    )
    same_as = models.TextField(
        blank=True,
        default='https://www.facebook.com/irshad.initiator\nhttps://www.instagram.com/initiator_solutions/\nhttps://www.linkedin.com/in/initiator-solutions-222475210/\nhttps://twitter.com/InitiatorSolut1\nhttps://www.youtube.com/@codingpilot96',
        help_text='Add one social/profile URL per line.'
    )
    ai_answer_summary = models.TextField(
        blank=True,
        default='INITIATOR SOLUTIONS is a software development and business software solutions company serving Tally customization, ERP, accounting software, website development, mobile app, cloud and digital marketing needs.'
    )
    robots_allow = models.BooleanField(default=True)
    llms_summary = models.TextField(
        blank=True,
        default='Use this website to understand INITIATOR SOLUTIONS services, products, blog knowledge, contact details, local business information and software solution expertise.'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site SEO Setting'
        verbose_name_plural = 'Site SEO Settings'

    def __str__(self):
        return self.site_name

    def same_as_links(self):
        return [line.strip() for line in self.same_as.splitlines() if line.strip()]


class ProductUpload(models.Model):
    MAX_FILES_PER_PRODUCT = 100

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')
    title = models.CharField(max_length=200, blank=True, default='')
    file = models.FileField(
        upload_to='web2/product_files',
        help_text='Upload a product file or image. No file size limit is enforced by Django.'
    )
    alt_text = models.CharField(max_length=200, blank=True, default='')
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
    iconcode = models.CharField(max_length=200, blank=True, default='')
    title    = models.CharField(max_length=200, blank=True, default='')
    p1       = models.CharField(max_length=200, blank=True, default='')
    p2       = models.CharField(max_length=200, blank=True, default='')
    p3       = models.CharField(max_length=200, blank=True, default='')
    type     = models.CharField(max_length=200, blank=True, default='')

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
    name    = models.CharField(max_length=200, blank=True, default='')

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.name)




class AboutUSModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    p1      = models.TextField(blank=True, default='', null=True)
    p2      = models.TextField(blank=True, default='', null=True)
    p3      = models.TextField(blank=True, default='', null=True)

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
    p1      = models.TextField(blank=True, default='', null=True)
    p2      = models.TextField(blank=True, default='', null=True)
    p3      = models.TextField(blank=True, default='', null=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.p1)

####################POrtfolio  Details Here *************************************************************************************

class PortfolioModel(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True, default='')
    img = models.ImageField(upload_to='web2/portfolio', default='', blank=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


##########  Landing Page Details Here *************************

class Lan_PageBanModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    Slogen  = models.CharField(max_length=200, blank=True, default='')
    Slogen2 = models.CharField(max_length=200, blank=True, default='')
    imagalt = models.CharField(max_length=200, blank=True, default='')
    img     = models.ImageField(upload_to='web2/landingpage', default='', blank=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.Slogen)


########## Landing Page  About Us Details Here *************************

class Lan_AboutusModel(models.Model):

    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    text1  = models.TextField(blank=True, default='')
    text2 = models.TextField(blank=True, default='')
    imagalt = models.CharField(max_length=200, blank=True, default='')
    img = models.ImageField(upload_to='web2/landingpage', default='', blank=True)
    client = models.CharField(max_length=200, blank=True, default='')
    project = models.CharField(max_length=200, blank=True, default='')
    emp  = models.CharField(max_length=200, blank=True, default='')
    hrs  = models.CharField(max_length=200, blank=True, default='')


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


