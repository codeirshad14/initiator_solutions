import json
import logging
import re
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.mail import BadHeaderError, send_mail
from django.core.validators import validate_email
from django.db import OperationalError, ProgrammingError
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone

from web2.context_processors import schema_json as _schema_json
from web2.models import Blog, ContactModel, \
    WebDevModel, AboutUSModel, AboutVisionModel, PortfolioModel, Web_DesignModel, \
    Web_Portal_Dev, MobileAppModel, Tally_Customization, Tally_VerticalModel, Tally_CloudModel, Digital_Mkt_Model, \
    Graphics_Model, CloudModel, OurNewsLetter, Lan_PageBanModel, Lan_AboutusModel, Lan_ServicesModel, \
    SiteSEO, Product, Service, ContactIntegrationSettings, CatalogGroup, plain_text_summary


logger = logging.getLogger('web2.errors')


def _site_seo():
  try:
    return SiteSEO.objects.first() or SiteSEO()
  except (OperationalError, ProgrammingError):
    return SiteSEO()


def _base_url(request):
  site_seo = _site_seo()
  return (site_seo.site_domain or request.build_absolute_uri('/')).rstrip('/')


def _absolute_url(request, path):
  if path.startswith(('http://', 'https://')):
    return path
  if path.startswith('/'):
    return f'{_base_url(request)}{path}'
  return f'{_base_url(request)}/{path}'


def _canonical_url(request, path):
  return _absolute_url(request, path)


def _organization_ref(request):
  # Matches the @id of the business entity output by context_processors.seo_context.
  return {'@id': f'{_base_url(request)}/#organization'}


def _webpage_schema(request, title, description, page_type='WebPage'):
  url = _canonical_url(request, request.path)
  return _schema_json({
    '@context': 'https://schema.org',
    '@type': page_type,
    '@id': f'{url}#webpage',
    'name': title,
    'description': description,
    'url': url,
    'inLanguage': 'en-IN',
    'isPartOf': {'@id': f'{_base_url(request)}/#website'},
    'publisher': _organization_ref(request),
  })


def _breadcrumb_schema(request, items):
  return _schema_json({
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    'itemListElement': [
      {
        '@type': 'ListItem',
        'position': index,
        'name': name,
        'item': _canonical_url(request, url),
      }
      for index, (name, url) in enumerate(items, start=1)
    ],
  })


def _blog_tags(blog):
  return [tag.strip() for tag in (blog.tags or blog.type or '').split(',') if tag.strip()]


def _blog_sidebar_context(exclude_blog_id=None):
  published_blogs = Blog.objects.filter(is_published=True)
  recent_posts = published_blogs.order_by('-pub_date', '-id')
  if exclude_blog_id:
    recent_posts = recent_posts.exclude(id=exclude_blog_id)
  all_tags = sorted({
    tag
    for blog in published_blogs
    for tag in _blog_tags(blog)
  })
  return {
    "recent_posts": recent_posts[:5],
    "categories": published_blogs.exclude(type='').order_by('type').values_list('type', flat=True).distinct(),
    "all_tags": all_tags,
  }


def _blog_article_schema(request, blog):
  image_url = _absolute_url(request, blog.image.url) if blog.image else ''
  url = _canonical_url(request, blog.get_absolute_url())
  author_name = (blog.author_name or '').strip()
  if author_name and author_name.lower() not in ('initiator team', _site_seo().organization_name.lower()):
    author = {'@type': 'Person', 'name': author_name}
  else:
    author = _organization_ref(request)
  return _schema_json({
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    'headline': blog.seo_title(),
    'description': blog.seo_description(),
    'image': image_url,
    'author': author,
    'publisher': _organization_ref(request),
    'datePublished': blog.pub_date.isoformat(),
    'dateModified': blog.updated_at.isoformat(),
    'mainEntityOfPage': {'@id': f'{url}#webpage'},
    'inLanguage': 'en-IN',
    'keywords': blog.seo_keywords(),
    'articleSection': blog.type,
  })


def _group_dict(group):
  return {
    'key': group.slug,
    'label': group.name,
  }


def _catalog_groups(group_type, **item_filter):
  # Only groups of this page's type that have at least one visible item.
  groups = CatalogGroup.objects.filter(group_type=group_type, **item_filter).distinct()
  return [_group_dict(group) for group in groups.order_by('sort_order', 'name')]


_FAQ_BLOCK = re.compile(r'<h3[^>]*>(.*?)</h3>(.*?)(?=<h[1-3][\s>]|$)', re.IGNORECASE | re.DOTALL)


def _faq_schema(content):
  # Heading 3 questions ending in "?" followed by their answer text become FAQPage
  # markup; it only describes questions that are visible on the page.
  questions = []
  for question_html, answer_html in _FAQ_BLOCK.findall(content or ''):
    question = plain_text_summary(question_html, limit=300)
    answer = plain_text_summary(answer_html, limit=1000)
    if question.endswith('?') and answer:
      questions.append({
        '@type': 'Question',
        'name': question,
        'acceptedAnswer': {'@type': 'Answer', 'text': answer},
      })
  if len(questions) < 2:
    return ''
  return _schema_json({
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    'mainEntity': questions,
  })


def _product_groups():
  return _catalog_groups(
    CatalogGroup.TYPE_PRODUCT,
    products__show_in_catalog=True,
    products__is_published=True,
  )


def _product_catalog(group_key=''):
  products = Product.objects.filter(
    show_in_catalog=True,
    is_published=True,
  ).select_related('product_group')
  if group_key:
    products = products.filter(product_group__slug=group_key)
  return [
    {
      'product': product,
      'group_key': product.product_group.slug,
      'group_label': product.product_group.name,
      'detail_url': product.get_absolute_url(),
    }
    for product in products.order_by('product_group__sort_order', 'product_group__name', 'sort_order', 'id')
  ]


def _service_groups():
  return _catalog_groups(
    CatalogGroup.TYPE_SERVICE,
    services__show_in_services=True,
    services__is_published=True,
  )


def _module_service_groups():
  return _catalog_groups(
    CatalogGroup.TYPE_MODULE,
    module_services__show_on_module_page=True,
    module_services__is_published=True,
  )


def _service_catalog(group_key='', module_only=False, landing_only=False):
  services = Service.objects.filter(is_published=True).select_related('service_group', 'module_group')
  if module_only:
    services = services.filter(show_on_module_page=True)
    if group_key:
      services = services.filter(module_group__slug=group_key)
  else:
    if landing_only:
      services = services.filter(show_on_landing=True)
    else:
      services = services.filter(show_in_services=True)
    if group_key:
      services = services.filter(service_group__slug=group_key)

  items = []
  for service in services.order_by('sort_order', 'id'):
    group = service.module_group if module_only and service.module_group else service.service_group
    items.append({
      'service': service,
      'group_key': group.slug,
      'group_label': group.name,
      'detail_url': service.get_absolute_url(),
    })
  return items


def _service_schema(request, service):
  image_url = _absolute_url(request, service.img.url) if service.img else ''
  url = _canonical_url(request, service.get_absolute_url())
  return _schema_json({
    '@context': 'https://schema.org',
    '@type': 'Service',
    'name': service.seo_title(),
    'description': service.seo_description(),
    'image': image_url,
    'url': url,
    'serviceType': service.service_group.name,
    'provider': _organization_ref(request),
    'areaServed': _site_seo().service_area,
    'keywords': service.seo_keywords(),
  })


def _product_schema(request, product):
  image_url = _absolute_url(request, product.img.url) if product.img else ''
  return _schema_json({
    '@context': 'https://schema.org',
    '@type': 'Product',
    'name': product.display_title(),
    'description': product.seo_description(),
    'category': product.product_group.name,
    'url': _canonical_url(request, product.get_absolute_url()),
    'image': image_url,
    # No "brand": most products (Tally, SAP, Busy, Zoho) are made by other
    # companies; claiming our own brand would mislead search and AI answers.
  })


# Create your views here.

def wbase(request):
  return render(request, 'web2/wbase.html')

#########  Welcome Page Initiator Solutions Index Page $$$$$$$$$$$

def index(request):

  lanbanpage = Lan_PageBanModel.objects.all()
  aboutus    = Lan_AboutusModel.objects.all()
  product    = Product.objects.filter(show_on_landing=True, is_published=True).select_related('product_group').order_by('sort_order', 'id')
  services   = Service.objects.filter(show_on_landing=True, is_published=True).select_related('service_group').order_by('sort_order', 'id')
  cont_list  = ContactModel.objects.all()

  seo_title = _site_seo().default_title
  seo_description = _site_seo().default_description
  context    = {
    "lanbanpage": lanbanpage,
    "aboutus":aboutus,
    "product":product,
    "services":services,
    "cont_list":cont_list,
    "seo_title": seo_title,
    "seo_description": seo_description,
    "seo_keywords": _site_seo().default_keywords,
    "seo_canonical_url": _canonical_url(request, reverse("index")),
    "webpage_schema_json": _webpage_schema(request, seo_title, seo_description),
  }

  return render(request, 'web2/index.html',context) 


############product
def web_product(request):
  group_key = request.GET.get('group', '')
  valid_groups = {group['key'] for group in _product_groups()}
  if group_key not in valid_groups:
    group_key = ''
  active_group = next((group for group in _product_groups() if group['key'] == group_key), None)
  context = {
    "product_items": _product_catalog(group_key),
    "product_groups": _product_groups(),
    "active_group": group_key,
    "page_heading": active_group['label'] if active_group else "All Products",
    "seo_title": "Tally Prime, Accounting & ERP Software | Initiator Solutions",
    "seo_description": "View Initiator Solutions products including Tally Prime, accounting software, ERP software, SAP, Busy, Zoho Books and custom business solutions.",
    "seo_keywords": "Tally Prime, accounting software, ERP software, SAP, Busy, Zoho Books, Initiator Solutions products",
    "seo_noindex": bool(group_key),
    "seo_canonical_url": _canonical_url(request, reverse("web_product")),
    "breadcrumb_schema_json": _breadcrumb_schema(request, [
      ("Home", reverse("index")),
      ("Products", reverse("web_product")),
    ]),
  }
  context["webpage_schema_json"] = _webpage_schema(request, context["seo_title"], context["seo_description"])
  return render(request,'web2/product/web_product.html',context)


def product_detail(request, group, id):
  product = get_object_or_404(
    Product.objects.select_related('product_group'),
    id=id,
    product_group__slug=group,
    is_published=True,
  )
  product_group = _group_dict(product.product_group)
  product_name = product.name or product.title
  description = product.seo_description()
  image_url = _absolute_url(request, product.img.url) if product.img else ''
  context = {
    "product": product,
    "product_group": product_group,
    "seo_title": product.seo_title(),
    "seo_description": description,
    "seo_keywords": product.seo_keywords(),
    "seo_image": image_url,
    "seo_noindex": not product.allow_index,
    "seo_canonical_url": product.canonical_url or _canonical_url(request, product.get_absolute_url()),
    "breadcrumb_schema_json": _breadcrumb_schema(request, [
      ("Home", reverse("index")),
      ("Products", reverse("web_product")),
      (product.display_title(), product.get_absolute_url()),
    ]),
    "product_schema_json": _product_schema(request, product),
    "faq_schema_json": _faq_schema(product.description or product.short_description),
  }
  context["webpage_schema_json"] = _webpage_schema(request, product.seo_title(), description)
  return render(request, 'web2/product/product_detail.html', context)


def _forward_contact_to_crm(request, enquiry):
  try:
    integration = ContactIntegrationSettings.objects.first()
  except (OperationalError, ProgrammingError):
    return False

  if not integration or not integration.is_enabled or not integration.endpoint_url:
    return False

  payload = {
    'lead_source': 'Website Contact Form',
    'source_url': request.build_absolute_uri(request.META.get('HTTP_REFERER') or request.path),
    'submitted_at': timezone.now().isoformat(),
    'provider': integration.provider_name,
    'name': enquiry.get('name', ''),
    'company_name': enquiry.get('cmpname', ''),
    'mobile': enquiry.get('mob', ''),
    'email': enquiry.get('email', ''),
    'subject': enquiry.get('subject', ''),
    'message': enquiry.get('message', ''),
  }
  headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'User-Agent': 'InitiatorSolutionsWebsite/1.0',
  }
  if integration.api_key and integration.auth_header_name:
    api_value = f'{integration.auth_token_prefix} {integration.api_key}'.strip()
    headers[integration.auth_header_name] = api_value
  if integration.extra_headers:
    try:
      extra_headers = json.loads(integration.extra_headers)
      if isinstance(extra_headers, dict):
        headers.update({str(key): str(value) for key, value in extra_headers.items()})
    except (TypeError, ValueError):
      integration.last_status = 'Failed: extra_headers is not valid JSON.'
      integration.last_sent_at = timezone.now()
      integration.save(update_fields=['last_status', 'last_sent_at', 'update_time'])
      return False

  data = json.dumps(payload).encode('utf-8')
  req = urlrequest.Request(integration.endpoint_url, data=data, headers=headers, method='POST')
  try:
    with urlrequest.urlopen(req, timeout=integration.timeout_seconds) as response:
      body = response.read(1200).decode('utf-8', errors='ignore')
      integration.last_status = f'Success: HTTP {response.status}'
      integration.last_response = body[:1200]
      integration.last_sent_at = timezone.now()
      integration.save(update_fields=['last_status', 'last_response', 'last_sent_at', 'update_time'])
      return True
  except HTTPError as error:
    body = error.read(1200).decode('utf-8', errors='ignore')
    integration.last_status = f'Failed: HTTP {error.code}'
    integration.last_response = body[:1200]
  except (URLError, TimeoutError, ValueError) as error:
    integration.last_status = f'Failed: {error}'
    integration.last_response = ''

  integration.last_sent_at = timezone.now()
  integration.save(update_fields=['last_status', 'last_response', 'last_sent_at', 'update_time'])
  return False

####All Accounting Software
def allaccounting_software(request):
  return redirect(f'{reverse("web_product")}?group=accounting-software')


####All Other ERP  Software
def allerp_software(request):
  return redirect(f'{reverse("web_product")}?group=erp-software')


#######contact email  form  view  details
def contact_email(request):
  if request.method == 'POST':
    data = {
      field: request.POST.get(field, '').strip()
      for field in ('name', 'cmpname', 'mob', 'email', 'subject', 'message')
    }
    # Email headers cannot contain line breaks.
    subject = ' '.join(data['subject'].split()) or 'New Website Enquiry'

    message = (
      f"New Enquiry NAME-- {data['name']} Email-- {data['email']} "
      f"Company Name--{data['cmpname']} Mobile No-- {data['mob']} "
      f"Subject-- {data['subject']} Message-- {data['message']}"
    )
    try:
      send_mail(subject, message, '', ['solutionsinitiator1@gmail.com'])
    except (BadHeaderError, OSError):
      logger.exception('Contact enquiry email failed for email=%s', data['email'])
    _forward_contact_to_crm(request, data)
  return redirect('contact')

############END product
##########################BLOG Views*************

def homeblog(request):

  blog = Blog.objects.filter(is_published=True).order_by('-pub_date', '-id')
  keyword = request.GET.get('keyword', '').strip()

  if keyword:
    blog = Blog.objects.filter(is_published=True).filter(
      Q(title__icontains=keyword) |
      Q(body__icontains=keyword) |
      Q(type__icontains=keyword) |
      Q(tags__icontains=keyword) |
      Q(focus_keyword__icontains=keyword)
    ).order_by('-pub_date', '-id')
  context = {
    "blog": blog,
    "active_keyword": keyword,
    "blog_count": blog.count(),
    "featured_blog": blog.first(),
    "seo_title": "Initiator Solutions Blog",
    "seo_description": "Read Initiator Solutions blog posts on Tally customization, accounting software, ERP, website development, mobile apps, cloud and digital marketing.",
    "seo_keywords": "initiator solutions blog, tally blog, ERP blog, accounting software blog, software development blog",
    "seo_noindex": bool(keyword),
    "seo_canonical_url": _canonical_url(request, reverse("homeblog")),
    "breadcrumb_schema_json": _breadcrumb_schema(request, [
      ("Home", reverse("index")),
      ("Blog", reverse("homeblog")),
    ]),
  }
  context["webpage_schema_json"] = _webpage_schema(request, context["seo_title"], context["seo_description"], "Blog")
  context.update(_blog_sidebar_context())
  return render(request, 'web2/blog/homeblog.html', context)

def blog_single(request, id=None, slug=None):

  if slug:
    blog = get_object_or_404(Blog, slug=slug, is_published=True)
  else:
    blog = get_object_or_404(Blog, id=id, is_published=True)
    if blog.slug:
      # One URL per post: old /blog_single/<id>/ links move to the slug URL.
      return redirect(blog.get_absolute_url(), permanent=True)

  image_url = request.build_absolute_uri(blog.image.url) if blog.image else ''
  context = {
    "blog": blog,
    "blog_count": '',
    "active_keyword": '',
    "seo_title": blog.seo_title(),
    "seo_description": blog.seo_description(),
    "seo_keywords": blog.seo_keywords(),
    "seo_image": image_url,
    "seo_type": "article",
    "seo_author": blog.author_name or "Initiator Team",
    "seo_noindex": not blog.allow_index,
    "seo_canonical_url": blog.canonical_url or _canonical_url(request, blog.get_absolute_url()),
    "seo_published_time": blog.pub_date,
    "seo_modified_time": blog.updated_at,
    "seo_section": blog.type,
    "seo_tags": _blog_tags(blog),
    "article_schema_json": _blog_article_schema(request, blog),
    "faq_schema_json": _faq_schema(blog.body),
    "breadcrumb_schema_json": _breadcrumb_schema(request, [
      ("Home", reverse("index")),
      ("Blog", reverse("homeblog")),
      (blog.title, blog.get_absolute_url()),
    ]),
  }
  context["webpage_schema_json"] = _webpage_schema(request, blog.seo_title(), blog.seo_description())
  context.update(_blog_sidebar_context(blog.id))

  return render(request, 'web2/blog/blog_single.html', context)




#########All home Search  Details
##########################END   BLOG Views*******
#######contact Page Details
def contact(request):
  cont_list             = ContactModel.objects.all()
  try:
    contact_integration = ContactIntegrationSettings.objects.first()
  except (OperationalError, ProgrammingError):
    contact_integration = None
  seo_title = "Contact Initiator Solutions - Sector 2, Noida"
  seo_description = "Address, phone, email and map for Initiator Solutions, Sector 2, Noida, Uttar Pradesh 201301."
  context               = {
    "cont_list":cont_list,
    "contact_integration":contact_integration,
    "seo_title": seo_title,
    "seo_description": seo_description,
    "seo_keywords": "contact Initiator Solutions, software development company Noida, Tally customization contact, ERP solutions contact",
    "seo_canonical_url": _canonical_url(request, reverse("contact")),
    "breadcrumb_schema_json": _breadcrumb_schema(request, [
      ("Home", reverse("index")),
      ("Contact", reverse("contact")),
    ]),
    "webpage_schema_json": _webpage_schema(request, seo_title, seo_description, "ContactPage"),
  }
  return render(request, 'web2/contact.html',context)

#######END contact Page Details

########### ALl About Details here Here
#########SERVICE DETAILS HERE $$$$$$$$$$$$$$$$$$$$$$$$


#########SERVICE Web Portal $$$$$$$$$$$$$$$$$$$$$$$$

def web_dev(request):
  group_key = request.GET.get('group', '')
  valid_groups = {group['key'] for group in _service_groups()}
  if group_key not in valid_groups:
    group_key = ''
  active_group = next((group for group in _service_groups() if group['key'] == group_key), None)
  context = {
    "service_items": _service_catalog(group_key),
    "service_groups": _service_groups(),
    "active_group": group_key,
    "page_heading": active_group['label'] if active_group else "All Services",
    "seo_title": "Tally, Zoho & Web Development Services | Initiator Solutions",
    "seo_description": "TallyPrime customization, integration, Tally on Cloud, Tally AI, Tally course, Zoho and web development services from Initiator Solutions, Noida.",
    "seo_keywords": "website development, Tally customization, Tally integration, ERP services, cloud services, mobile app development, digital marketing, Initiator Solutions services",
    "seo_noindex": bool(group_key),
    "seo_canonical_url": _canonical_url(request, reverse("web_dev")),
    "breadcrumb_schema_json": _breadcrumb_schema(request, [
      ("Home", reverse("index")),
      ("Services", reverse("web_dev")),
    ]),
  }
  context["webpage_schema_json"] = _webpage_schema(request, context["seo_title"], context["seo_description"], "CollectionPage")
  return render(request,'web2/service/web_dev.html',context)


def service_detail(request, group, id):
  service = get_object_or_404(
    Service.objects.select_related('service_group'),
    id=id,
    service_group__slug=group,
    is_published=True,
  )
  service_group = _group_dict(service.service_group)
  image_url = _absolute_url(request, service.img.url) if service.img else ''
  from_modules = request.GET.get('from') == 'modules' and service.show_on_module_page
  context = {
    "service": service,
    "service_group": service_group,
    "detail_back_url": reverse("our_module_services") if from_modules else reverse("web_dev"),
    "detail_back_label": "All Modules" if from_modules else "All Services",
    "seo_title": service.seo_title(),
    "seo_description": service.seo_description(),
    "seo_keywords": service.seo_keywords(),
    "seo_image": image_url,
    "seo_noindex": not service.allow_index,
    "seo_canonical_url": service.canonical_url or _canonical_url(request, service.get_absolute_url()),
    "service_schema_json": _service_schema(request, service),
    "faq_schema_json": _faq_schema(service.description or service.short_description),
    "breadcrumb_schema_json": _breadcrumb_schema(request, [
      ("Home", reverse("index")),
      ("Services", reverse("web_dev")),
      (service.display_title(), service.get_absolute_url()),
    ]),
  }
  context["webpage_schema_json"] = _webpage_schema(request, service.seo_title(), service.seo_description())
  return render(request, 'web2/service/service_detail.html', context)


def _service_redirect(group_key):
  return redirect(f'{reverse("web_dev")}?group={group_key}')

########  Web design  View  Details ************************

def web_design(request):
  return _service_redirect(Service.GROUP_WEB_DESIGNING)

##  All #####Web Design  Portal  Development

def web_port_dev(request):
  return _service_redirect(Service.GROUP_WEB_PORTAL)

##### Mobile App  Development %%%%%%%%%%%%%%%%%%%%%%%%%%

def mob_appdev(request):
  return _service_redirect(Service.GROUP_MOBILE_APP)


##### Tally  Vertical  customization Details %%%%%%%%%%%%%%%%%%%%%%%%%%
def tally_customization(request):
  return _service_redirect(Service.GROUP_TALLY_CUSTOMIZATION)


##### Tally  Vertical  Solutions %%%%%%%%%%%%%%%%%%%%%%%%%%
def tally_ver_Solutions(request):
  return _service_redirect(Service.GROUP_TALLY_VERTICAL)

##### Tally On cloud  %%%%%%%%%%%%%%%%%%%%%%%%%%
def tally_cloud(request):
  return _service_redirect(Service.GROUP_TALLY_CLOUD)


##### Digital Marketing  %%%%%%%%%%%%%%%%%%%%%%%%%%
def digi_mkt(request):
  return _service_redirect(Service.GROUP_DIGITAL_MARKETING)




##### Graphics Design  %%%%%%%%%%%%%%%%%%%%%%%%%%
def graphics_design(request):
  return _service_redirect(Service.GROUP_GRAPHICS)



##### Cloud Only   %%%%%%%%%%%%%%%%%%%%%%%%%%
def cloud_services(request):
  return _service_redirect(Service.GROUP_CLOUD)




##### Module Design Here Design  %%%%%%%%%%%%%%%%%%%%%%%%%%
def our_module_services(request):
  group_key = request.GET.get('group', '')
  service_groups = _module_service_groups()
  valid_groups = {group['key'] for group in service_groups}
  if group_key not in valid_groups:
    group_key = ''
  active_group = next((group for group in service_groups if group['key'] == group_key), None)
  context = {
    "service_items": _service_catalog(group_key, module_only=True),
    "service_groups": service_groups,
    "active_group": group_key,
    "page_heading": active_group['label'] if active_group else "Our Modules",
    "seo_title": "Our Modules - Special Business Software Services",
    "seo_description": "View special Initiator Solutions service modules including Tally modules, barcode, approval, e-commerce integration and custom business workflows.",
    "seo_keywords": "Tally modules, business modules, barcode module, approval system, e-commerce Tally integration, custom software modules",
    "seo_noindex": bool(group_key),
    "seo_canonical_url": _canonical_url(request, reverse("our_module_services")),
    "breadcrumb_schema_json": _breadcrumb_schema(request, [
      ("Home", reverse("index")),
      ("Services", reverse("web_dev")),
      ("Our Modules", reverse("our_module_services")),
    ]),
  }
  context["webpage_schema_json"] = _webpage_schema(request, context["seo_title"], context["seo_description"], "CollectionPage")
  return render(request,'web2/service/our_module_services.html',context)



#### news latter
def news_letter(request):
  if request.method == 'POST':
    # The footer form posts the subscriber's email in the "name" field.
    email = request.POST.get('name', '').strip().lower()
    try:
      validate_email(email)
    except ValidationError:
      return redirect('index')
    max_length = OurNewsLetter._meta.get_field('name').max_length
    if len(email) <= max_length and not OurNewsLetter.objects.filter(name__iexact=email).exists():
      OurNewsLetter.objects.create(name=email)
  return redirect('index')

######### WHO WE ARE ##################################################################################################

def aboutus(request):

  #aboutus_title_list             = AboutUSModel_Title.objects.all()
  aboutus                         = AboutUSModel.objects.all()
  #aboutvision_title_list         = AboutVisionModel_Title.objects.all()
  aboutusvision                   = AboutVisionModel.objects.all()

  seo_title = "About Initiator Solutions - Noida Software Company"
  seo_description = "About Initiator Solutions, a Sector 2, Noida software company for TallyPrime customization, Tally integration, Tally on Cloud, Zoho and web development."
  context        = {
    "aboutus":aboutus,
    "aboutusvision":aboutusvision,
    "seo_title": seo_title,
    "seo_description": seo_description,
    "seo_keywords": "about Initiator Solutions, software development company, Tally solutions company, ERP solutions",
    "seo_canonical_url": _canonical_url(request, reverse("aboutus")),
    "breadcrumb_schema_json": _breadcrumb_schema(request, [
      ("Home", reverse("index")),
      ("About", reverse("aboutus")),
    ]),
    "webpage_schema_json": _webpage_schema(request, seo_title, seo_description, "AboutPage"),
  }
  return render(request,'web2/aboutus.html',context)

######### END WHO WE ARE ##############################################################################################

######### Portfolio  START##################################################################################################

def portfolio(request):

  portfolio_one    = PortfolioModel.objects.all().order_by('id')
  portfolio_stats  = Lan_AboutusModel.objects.first()
  landing_banner   = Lan_PageBanModel.objects.first()
  portfolio_cases = {
    'tally invoice customization': {
      'category': 'Tally Customization',
      'summary': 'Custom invoice formats, GST-ready print layouts and business-specific voucher controls for faster billing.',
      'outcome': 'Cleaner invoicing, fewer manual edits and better accounting document control.',
      'tags': ['Tally Prime', 'GST Invoice', 'Voucher Control'],
    },
    'e-commerce tally integration': {
      'category': 'Integration',
      'summary': 'Connected online orders, inventory and accounting data with Tally for smoother sales operations.',
      'outcome': 'Reduced duplicate entry and stronger order-to-accounting visibility.',
      'tags': ['E-Commerce', 'Inventory', 'Tally API'],
    },
    'garments module software': {
      'category': 'ERP Module',
      'summary': 'Garment business workflow module for products, stock, sales, purchase and role-based operations.',
      'outcome': 'Better stock tracking and more organized production/sales workflow.',
      'tags': ['Garments', 'ERP', 'Stock'],
    },
    'auto backup for tally': {
      'category': 'Automation',
      'summary': 'Automated Tally backup utility built to protect accounting data with scheduled backup discipline.',
      'outcome': 'Safer business data and less dependency on manual backup routines.',
      'tags': ['Backup', 'Automation', 'Data Safety'],
    },
    'barcode and label printing': {
      'category': 'Operations',
      'summary': 'Barcode and label printing workflow for inventory identification, packing and retail operations.',
      'outcome': 'Faster item handling, cleaner labels and improved stock movement control.',
      'tags': ['Barcode', 'Labels', 'Inventory'],
    },
    'approval system module': {
      'category': 'Workflow',
      'summary': 'Approval workflow module for controlled business decisions, document movement and team accountability.',
      'outcome': 'More transparent approval flow with stronger role-based process control.',
      'tags': ['Approval', 'Workflow', 'Control'],
    },
  }
  portfolio_items = []
  for project in portfolio_one:
    case = portfolio_cases.get((project.name or '').strip().lower(), {
      'category': 'Business Software',
      'summary': 'Custom software solution designed around business process, reporting and daily team use.',
      'outcome': 'Improved operational clarity and smoother day-to-day execution.',
      'tags': ['Software', 'Business', 'Support'],
    })
    portfolio_items.append({
      'project': project,
      **case,
    })
  context        = {
    "portfolio_one":portfolio_one,
    "portfolio_items":portfolio_items,
    "portfolio_stats":portfolio_stats,
    "landing_banner":landing_banner,
    "seo_title": "Our Portfolio - Initiator Solutions",
    "seo_description": "View Initiator Solutions portfolio examples for Tally customization, business software, e-commerce integration, automation and ERP modules.",
    "seo_keywords": "Initiator Solutions portfolio, Tally customization case study, business software projects, ERP modules",
    "seo_canonical_url": _canonical_url(request, reverse("portfolio")),
    "breadcrumb_schema_json": _breadcrumb_schema(request, [
      ("Home", reverse("index")),
      ("Portfolio", reverse("portfolio")),
    ]),
  }
  context["webpage_schema_json"] = _webpage_schema(request, context["seo_title"], context["seo_description"], "CollectionPage")
  return render(request,'web2/portfolio.html',context)


######### Portfolio  END##################################################################################################
######### Portfolio  END##################################################################################################


def robots_txt(request):
  site_seo = _site_seo()
  base = _base_url(request)
  if site_seo.robots_allow:
    lines = [
      'User-agent: *',
      'Allow: /',
      'Allow: /static/',
      'Allow: /media/',
      'Disallow: /admin/',
      'Disallow: /static/admin/',
      'Disallow: /web2/contact_email',
      'Disallow: /web2/news_letter',
      'Disallow: /*?keyword=',
      'Disallow: /*?group=',
      'Disallow: /*?*utm_',
    ]
  else:
    lines = [
      'User-agent: *',
      'Disallow: /',
    ]
  lines.extend([
    f'Sitemap: {base}{reverse("sitemap_xml")}',
    f'Host: {base.replace("https://", "").replace("http://", "")}',
  ])
  return HttpResponse('\n'.join(lines), content_type='text/plain')


def _llms_link(base, title, url, description=''):
  line = f'- [{title}]({base}{url})'
  return f'{line}: {description}' if description else line


def llms_txt(request):
  # Format follows https://llmstxt.org: H1 name, "> summary", then link lists.
  site_seo = _site_seo()
  base = _base_url(request)
  lines = [
    f'# {site_seo.site_name}',
    '',
    f'> {site_seo.ai_answer_summary}',
    '',
  ]
  if site_seo.llms_summary:
    lines.extend([site_seo.llms_summary, ''])
  lines.extend([
    '## Business profile',
    f'- Organization: {site_seo.organization_name}',
    f'- Website: {base}/',
    f'- Email: {site_seo.email}',
    f'- Phone: {site_seo.phone}',
    f'- Address: {site_seo.street_address}, {site_seo.locality}, {site_seo.region} {site_seo.postal_code}, {site_seo.country}',
    f'- Service area: {site_seo.service_area}',
  ])
  if site_seo.opening_hours:
    lines.append(f'- Opening hours: {site_seo.opening_hours}')

  sections = [
    ('Products', [item['product'] for item in _product_catalog()]),
    ('Services', [item['service'] for item in _service_catalog()]),
    ('Our Modules', [item['service'] for item in _service_catalog(module_only=True)]),
  ]
  for heading, items in sections:
    items = [item for item in items if item.allow_index]
    if items:
      lines.extend(['', f'## {heading}'])
      lines.extend(
        _llms_link(base, item.display_title(), item.get_absolute_url(), item.seo_description())
        for item in items
      )

  blogs = Blog.objects.filter(is_published=True, allow_index=True).order_by('-pub_date', '-id')[:20]
  if blogs:
    lines.extend(['', '## Blog'])
    lines.extend(_llms_link(base, blog.title, blog.get_absolute_url(), blog.seo_description()) for blog in blogs)

  lines.extend([
    '',
    '## Company',
    _llms_link(base, 'About / Who We Are', reverse('aboutus')),
    _llms_link(base, 'Portfolio', reverse('portfolio')),
    _llms_link(base, 'Contact', reverse('contact'), 'Phone, email, address, map and enquiry form'),
    '',
    '## Optional',
    _llms_link(base, 'Sitemap', reverse('sitemap_xml')),
  ])
  return HttpResponse('\n'.join(lines) + '\n', content_type='text/plain; charset=utf-8')


def favicon(request):
  return redirect(static('web2/assets/img/logo/NW/InitiatorLogo-favicon-96x96.png'), permanent=True)


def indexnow_key_file(request, key):
  site_seo = _site_seo()
  if not site_seo.indexnow_enabled or not site_seo.indexnow_key or key != site_seo.indexnow_key:
    raise Http404('No IndexNow key')
  return HttpResponse(key, content_type='text/plain; charset=utf-8')


def llm_txt(request):
  return llms_txt(request)


def _error_diagnostic_context(request, status_code, exception=None):
  diagnostic_id = uuid4().hex[:12].upper()
  requested_path = request.get_full_path()
  referrer = request.META.get('HTTP_REFERER') or 'Not sent'
  user_agent = request.META.get('HTTP_USER_AGENT') or 'Not sent'
  exception_message = str(exception or '').strip()

  if request.path.startswith(('/static/', '/media/')):
    public_reason = 'The requested file path does not exist or is no longer available.'
  elif exception_message.startswith('No '):
    public_reason = 'The URL exists, but the requested item is not published or is no longer available.'
  elif status_code == 404:
    public_reason = 'No matching website route was found for this address.'
  else:
    public_reason = 'The website reached Django, but Django could not complete the request.'

  return {
    'diagnostic_id': diagnostic_id,
    'requested_path': requested_path,
    'request_method': request.method,
    'referrer': referrer,
    'user_agent': user_agent[:180],
    'public_reason': public_reason,
  }


def custom_404(request, exception):
  seo_title = "Page Not Found - INITIATOR SOLUTIONS"
  seo_description = "The requested page could not be found on Initiator Solutions."
  diagnostics = _error_diagnostic_context(request, 404, exception)
  logger.warning(
    '404 page not found diagnostic_id=%s method=%s path=%s referrer=%s user_agent=%s exception=%r',
    diagnostics['diagnostic_id'],
    diagnostics['request_method'],
    diagnostics['requested_path'],
    diagnostics['referrer'],
    diagnostics['user_agent'],
    exception,
  )
  context = {
    "seo_title": seo_title,
    "seo_description": seo_description,
    "seo_keywords": "page not found, Initiator Solutions",
    "seo_noindex": True,
    "seo_canonical_url": _canonical_url(request, request.path),
    "webpage_schema_json": _webpage_schema(request, seo_title, seo_description),
  }
  context.update(diagnostics)
  try:
    return render(request, '404.html', context, status=404)
  except Exception:
    logger.exception('404 page could not be rendered diagnostic_id=%s', diagnostics['diagnostic_id'])
    return _plain_error_response(404, 'Page not found', diagnostics['diagnostic_id'])


def _plain_error_response(status, title, diagnostic_id):
  # Last-resort page when the themed error page itself fails (e.g. database down).
  return HttpResponse(
    f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex">'
    f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} - Initiator Solutions</title></head>'
    f'<body style="font-family:Arial,sans-serif;max-width:640px;margin:60px auto;padding:0 16px;color:#012970">'
    f'<h1>{title}</h1><p>Please try again in a moment or go to the <a href="/">home page</a>.</p>'
    f'<p>Call <a href="tel:+918882595800">+91 88825 95800</a> or email '
    f'<a href="mailto:info@initiatorsolutions.com">info@initiatorsolutions.com</a>.</p>'
    f'<p style="color:#667085">Diagnostic ID: {diagnostic_id}</p></body></html>',
    status=status,
  )


def custom_500(request):
  seo_title = "Server Error - INITIATOR SOLUTIONS"
  seo_description = "A temporary server error occurred on Initiator Solutions."
  diagnostics = _error_diagnostic_context(request, 500)
  logger.error(
    '500 server error diagnostic_id=%s method=%s path=%s referrer=%s user_agent=%s',
    diagnostics['diagnostic_id'],
    diagnostics['request_method'],
    diagnostics['requested_path'],
    diagnostics['referrer'],
    diagnostics['user_agent'],
  )
  context = {
    "seo_title": seo_title,
    "seo_description": seo_description,
    "seo_keywords": "server error, Initiator Solutions",
    "seo_noindex": True,
    "seo_canonical_url": _canonical_url(request, request.path),
    "webpage_schema_json": _webpage_schema(request, seo_title, seo_description),
  }
  context.update(diagnostics)
  try:
    return render(request, '500.html', context, status=500)
  except Exception:
    logger.exception('500 page could not be rendered diagnostic_id=%s', diagnostics['diagnostic_id'])
    return _plain_error_response(500, 'Server error', diagnostics['diagnostic_id'])


