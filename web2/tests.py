import json
import re
import shutil
import tempfile
from io import BytesIO, StringIO
from pathlib import Path
from smtplib import SMTPException
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.core import mail
from django.core.management import CommandError, call_command
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from . import views
from django.core.exceptions import ValidationError

from . import indexnow, seo_content
from .admin import ProductAdminForm, ServiceAdminForm
from .models import (
    Blog, CatalogGroup, Lan_PageBanModel, OurNewsLetter, Product, ProductUpload, Service, SiteSEO, plain_text_summary,
)


def group(group_type, slug):
    # Default product/service groups are created by migration 0045.
    return CatalogGroup.objects.get(group_type=group_type, slug=slug)


class SEOEndpointTests(TestCase):
    def setUp(self):
        SiteSEO.objects.all().delete()
        self.site_seo = SiteSEO.objects.create(
            site_name='INITIATOR SOLUTIONS',
            site_domain='https://www.example.com',
            default_og_image='/static/web2/assets/img/logo/NW/InitiatorLogo.png',
        )
        self.user = User.objects.create_user(username='seo-user', password='pass')
        self.product = Product.objects.create(
            user=self.user,
            product_group=group(CatalogGroup.TYPE_PRODUCT, Product.GROUP_TALLY),
            name='Tally Prime',
            title='Tally Prime',
            short_description='Tally Prime support and implementation for growing businesses.',
            description='<p>Tally Prime support and implementation for growing businesses.</p>',
            show_in_catalog=True,
            is_published=True,
            allow_index=True,
            meta_title='Tally Prime | INITIATOR SOLUTIONS',
            meta_description='Tally Prime support and implementation from Initiator Solutions.',
        )
        self.service = Service.objects.create(
            user=self.user,
            service_group=group(CatalogGroup.TYPE_SERVICE, Service.GROUP_WEB_DEVELOPMENT),
            name='Website Development',
            title='Website Development',
            short_description='Business website development services.',
            description='<p>Business website development services.</p>',
            show_in_services=True,
            is_published=True,
            allow_index=True,
            meta_title='Website Development | INITIATOR SOLUTIONS',
            meta_description='Website development services from Initiator Solutions.',
        )
        self.module_service = Service.objects.create(
            user=self.user,
            service_group=group(CatalogGroup.TYPE_SERVICE, Service.GROUP_TALLY_VERTICAL),
            module_group=CatalogGroup.objects.create(
                group_type=CatalogGroup.TYPE_MODULE,
                name='Tally Vertical / Module Services',
                slug=Service.GROUP_TALLY_VERTICAL,
            ),
            name='Approval Workflow Module',
            title='Approval Workflow Module',
            short_description='Approval workflow module for business teams.',
            description='<p>Approval workflow module for business teams.</p>',
            show_in_services=False,
            show_on_module_page=True,
            is_published=True,
            allow_index=True,
            meta_title='Approval Workflow Module | INITIATOR SOLUTIONS',
            meta_description='Approval workflow module from Initiator Solutions.',
        )
        self.blog = Blog.objects.create(
            title='Tally Customization Tips',
            slug='tally-customization-tips',
            type='Tally',
            pub_date=timezone.now(),
            body='<p>Useful Tally customization tips for business teams.</p>',
            image='web2/blog/tally-customization-tips.jpg',
            alt='Tally customization tips',
            is_published=True,
            allow_index=True,
            meta_description='Useful Tally customization tips for business teams.',
        )

    def test_robots_txt_blocks_private_and_duplicate_urls(self):
        response = self.client.get(reverse('robots_txt'))

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('Allow: /static/', body)
        self.assertIn('Allow: /media/', body)
        self.assertIn('Disallow: /admin/', body)
        self.assertIn('Disallow: /web2/contact_email', body)
        self.assertIn('Disallow: /*?group=', body)
        self.assertIn('Disallow: /*?keyword=', body)
        self.assertIn('Sitemap: https://www.example.com/sitemap.xml', body)

    def test_sitemap_lists_canonical_public_urls(self):
        response = self.client.get(reverse('sitemap_xml'))

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn(f'https://www.example.com{self.product.get_absolute_url()}', body)
        self.assertIn(f'https://www.example.com{self.service.get_absolute_url()}', body)
        self.assertIn(f'https://www.example.com{self.blog.get_absolute_url()}', body)
        self.assertIn(reverse('web_product'), body)
        self.assertNotIn(reverse('allaccounting_software'), body)
        self.assertNotIn('?group=', body)
        self.assertNotIn('/admin/', body)

    def test_product_detail_has_canonical_schema_and_service_style_media(self):
        response = self.client.get(self.product.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn(
            f'<link rel="canonical" href="https://www.example.com{self.product.get_absolute_url()}">',
            body,
        )
        self.assertIn('"@type": "Product"', body)
        self.assertIn('"@type": "BreadcrumbList"', body)
        self.assertIn('<h1 style=', body)
        self.assertIn('product-detail-media', body)
        self.assertIn('no-image-placeholder no-image-detail', body)
        self.assertIn('No Image', body)
        self.assertNotIn('Product Images', body)
        self.assertEqual(body.count('name="description"'), 1)

    def test_upload_fields_do_not_enforce_file_size_validators(self):
        product_img_validators = Product._meta.get_field('img').validators
        blog_image_field = Blog._meta.get_field('image')
        upload_file_validators = ProductUpload._meta.get_field('file').validators

        self.assertEqual(product_img_validators, [])
        self.assertEqual(upload_file_validators, [])
        self.assertTrue(blog_image_field.blank)
        self.assertEqual(blog_image_field.default, '')

    def test_filter_pages_are_noindex_and_canonicalized(self):
        response = self.client.get(reverse('web_product'), {'group': Product.GROUP_TALLY})

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('<meta name="robots" content="noindex,follow">', body)
        self.assertIn(
            f'<link rel="canonical" href="https://www.example.com{reverse("web_product")}">',
            body,
        )

    def test_our_modules_filter_only_shows_module_groups(self):
        response = self.client.get(reverse('our_module_services'))

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('All Modules', body)
        self.assertIn(f'?group={Service.GROUP_TALLY_VERTICAL}', body)
        self.assertNotIn(f'?group={Service.GROUP_WEB_DEVELOPMENT}', body)
        self.assertIn('Approval Workflow Module', body)
        self.assertNotIn('Website Development</a></h3>', body)

        filtered_response = self.client.get(
            reverse('our_module_services'),
            {'group': Service.GROUP_TALLY_VERTICAL},
        )

        self.assertEqual(filtered_response.status_code, 200)
        filtered_body = filtered_response.content.decode()
        self.assertIn('<meta name="robots" content="noindex,follow">', filtered_body)
        self.assertIn(
            f'<link rel="canonical" href="https://www.example.com{reverse("our_module_services")}">',
            filtered_body,
        )

    @override_settings(DEBUG=False, ALLOWED_HOSTS=['testserver'])
    def test_custom_404_is_noindex(self):
        response = self.client.get('/missing-seo-page/')

        self.assertEqual(response.status_code, 404)
        body = response.content.decode()
        self.assertIn('Page Not Found', body)
        self.assertIn('<meta name="robots" content="noindex,follow">', body)
        self.assertIn('Requested URL', body)
        self.assertIn('/missing-seo-page/', body)
        self.assertIn('Likely reason', body)
        self.assertIn('Diagnostic ID', body)

    @override_settings(DEBUG=False, ALLOWED_HOSTS=['testserver'])
    def test_custom_500_returns_diagnostic_page(self):
        request = RequestFactory().get('/server-error-check/')

        response = views.custom_500(request)

        self.assertEqual(response.status_code, 500)
        body = response.content.decode()
        self.assertIn('Server Error', body)
        self.assertIn('Django-side server error', body)
        self.assertIn('/server-error-check/', body)
        self.assertIn('Diagnostic ID', body)
        self.assertIn('<meta name="robots" content="noindex,follow">', body)

    def test_custom_500_logs_the_full_traceback(self):
        request = RequestFactory().post('/admin/web2/product/5/change/')

        with self.assertLogs('web2.errors', 'ERROR') as logs:
            try:
                raise PermissionError(13, 'Permission denied', '/srv/static/dynamic_images/web2/product/x.png')
            except PermissionError:
                response = views.custom_500(request)

        self.assertEqual(response.status_code, 500)
        self.assertIn('Traceback (most recent call last)', logs.output[0])
        self.assertIn('PermissionError', logs.output[0])
        self.assertIn('/admin/web2/product/5/change/', logs.output[0])

    def test_static_502_page_exists_for_nginx_gateway_errors(self):
        error_page = Path(settings.BASE_DIR) / 'static' / 'error_pages' / '502.html'

        self.assertTrue(error_page.exists())
        body = error_page.read_text(encoding='utf-8')
        self.assertIn('502', body)
        self.assertIn('Bad Gateway', body)
        self.assertIn('nginx', body)


class CatalogGroupTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='group-user', password='pass')
        self.tally = group(CatalogGroup.TYPE_PRODUCT, Product.GROUP_TALLY)
        self.web_dev = group(CatalogGroup.TYPE_SERVICE, Service.GROUP_WEB_DEVELOPMENT)
        Product.objects.create(user=self.user, product_group=self.tally, name='Tally Prime')
        Service.objects.create(user=self.user, service_group=self.web_dev, name='Website Development')

    def filter_links(self, url_name):
        body = self.client.get(reverse(url_name)).content.decode()
        return set(re.findall(r'\?group=([a-z0-9-]+)"', body))

    def test_each_page_lists_only_its_own_groups_that_have_items(self):
        new_module = CatalogGroup.objects.create(group_type=CatalogGroup.TYPE_MODULE, name='Barcode Modules')
        Service.objects.create(
            user=self.user, service_group=self.web_dev, module_group=new_module,
            name='Barcode Module', show_in_services=False, show_on_module_page=True,
        )

        self.assertEqual(self.filter_links('web_product'), {'tally-prime'})
        self.assertEqual(self.filter_links('web_dev'), {'website-development'})
        self.assertEqual(self.filter_links('our_module_services'), {'barcode-modules'})

    def test_new_service_group_shows_on_services_page_with_working_detail_url(self):
        ai_group = CatalogGroup.objects.create(group_type=CatalogGroup.TYPE_SERVICE, name='AI Automation')
        service = Service.objects.create(user=self.user, service_group=ai_group, name='Chatbot Setup')

        self.assertEqual(ai_group.slug, 'ai-automation')
        self.assertIn('ai-automation', self.filter_links('web_dev'))
        self.assertNotIn('ai-automation', self.filter_links('web_product'))
        filtered = self.client.get(reverse('web_dev'), {'group': 'ai-automation'}).content.decode()
        self.assertIn('Chatbot Setup', filtered)
        self.assertNotIn('Website Development</a></h3>', filtered)
        self.assertEqual(service.get_absolute_url(), '/web2/service/ai-automation/%d/' % service.id)
        self.assertEqual(self.client.get(service.get_absolute_url()).status_code, 200)

    def test_new_product_group_shows_on_products_page(self):
        cloud = CatalogGroup.objects.create(group_type=CatalogGroup.TYPE_PRODUCT, name='Cloud Products')
        product = Product.objects.create(user=self.user, product_group=cloud, name='Cloud Server')

        self.assertIn('cloud-products', self.filter_links('web_product'))
        self.assertEqual(self.client.get(product.get_absolute_url()).status_code, 200)
        wrong_group_url = reverse('product_detail', kwargs={'group': 'tally-prime', 'id': product.id})
        self.assertEqual(self.client.get(wrong_group_url).status_code, 404)

    def test_admin_forms_only_offer_groups_of_matching_type(self):
        module = CatalogGroup.objects.create(group_type=CatalogGroup.TYPE_MODULE, name='Modules')
        product_choices = ProductAdminForm().fields['product_group'].queryset
        service_choices = ServiceAdminForm().fields['service_group'].queryset
        module_choices = ServiceAdminForm().fields['module_group'].queryset

        self.assertEqual({g.group_type for g in product_choices}, {CatalogGroup.TYPE_PRODUCT})
        self.assertEqual({g.group_type for g in service_choices}, {CatalogGroup.TYPE_SERVICE})
        self.assertEqual(list(module_choices), [module])

    def test_module_page_service_needs_module_group(self):
        service = Service(user=self.user, service_group=self.web_dev, name='X', show_on_module_page=True)

        with self.assertRaises(ValidationError) as error:
            service.clean()
        self.assertIn('module_group', error.exception.message_dict)

    def test_same_slug_allowed_for_different_group_types(self):
        module = CatalogGroup.objects.create(group_type=CatalogGroup.TYPE_MODULE, name='Website Development')
        duplicate = CatalogGroup.objects.create(group_type=CatalogGroup.TYPE_SERVICE, name='Website Development')

        self.assertEqual(module.slug, 'website-development')
        self.assertEqual(duplicate.slug, 'website-development-2')

    def test_group_admin_pages_load(self):
        User.objects.create_superuser(username='admin', password='pass', email='admin@example.com')
        self.client.login(username='admin', password='pass')

        self.assertEqual(self.client.get(reverse('admin:web2_cataloggroup_changelist')).status_code, 200)
        self.assertEqual(self.client.get(reverse('admin:web2_cataloggroup_add')).status_code, 200)
        self.assertEqual(self.client.get(reverse('admin:web2_service_add')).status_code, 200)
        self.assertEqual(self.client.get(reverse('admin:web2_product_add')).status_code, 200)


class SEOQualityTests(TestCase):
    def setUp(self):
        SiteSEO.objects.all().delete()
        self.site_seo = SiteSEO.objects.create(
            site_domain='https://www.example.com',
            default_title='Tally & Software Solutions in Noida | INITIATOR SOLUTIONS',
            default_description='INITIATOR SOLUTIONS is a Noida software company for Tally customization, ERP, websites and cloud.',
            founder_name='Test Founder',
        )
        user = User.objects.create_user(username='seo-quality', password='pass')
        # The home page H1 lives in the hero banner, which the live site always has.
        Lan_PageBanModel.objects.create(user=user, imagalt='Banner')
        self.product = Product.objects.create(
            user=user, product_group=group(CatalogGroup.TYPE_PRODUCT, Product.GROUP_TALLY), name='Tally Prime',
            description='<h1>Buy TallyPrime</h1><p>Licence and setup.</p><h1></h1>',
        )
        self.service = Service.objects.create(
            user=user, service_group=group(CatalogGroup.TYPE_SERVICE, Service.GROUP_WEB_DEVELOPMENT),
            name='Tally Prime', short_description='Tally&nbsp; Prime&nbsp;',
        )
        self.blog = Blog.objects.create(
            title='How to migrate Tally data', slug='migrate-tally-data', type='Tally',
            pub_date=timezone.now(), body='<p>Step by step guide.</p>',
        )

    def public_urls(self):
        return [
            reverse('index'), reverse('aboutus'), reverse('contact'), reverse('portfolio'),
            reverse('web_product'), reverse('web_dev'), reverse('our_module_services'), reverse('homeblog'),
            self.product.get_absolute_url(), self.service.get_absolute_url(), self.blog.get_absolute_url(),
        ]

    def test_every_page_has_one_h1_title_description_canonical_and_valid_schema(self):
        for url in self.public_urls():
            body = self.client.get(url).content.decode()
            with self.subTest(url=url):
                self.assertEqual(len(re.findall(r'<h1[\s>]', body)), 1)
                self.assertEqual(body.count('name="description"'), 1)
                description = re.search(r'<meta content="([^"]*)" name="description">', body).group(1)
                self.assertTrue(0 < len(description) <= 160, description)
                self.assertEqual(body.count('<link rel="canonical"'), 1)
                blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S)]
                ids = {b.get('@id') for b in blocks}
                self.assertIn('https://www.example.com/#organization', ids)
                self.assertIn('https://www.example.com/#website', ids)
                refs = re.findall(r'"@id": "(https://www\.example\.com/#[a-z]+)"', body)
                self.assertTrue(set(refs) <= ids, f'unresolved @id references {set(refs) - ids}')

    def test_organization_schema_is_one_local_business_entity(self):
        body = self.client.get(reverse('index')).content.decode()
        org = json.loads(re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S)[0])

        self.assertEqual(org['@type'], ['Organization', 'LocalBusiness'])
        self.assertEqual(org['founder']['name'], 'Test Founder')
        self.assertEqual(org['openingHours'], 'Mo-Fr 10:00-18:30')
        self.assertIn('Noida', org['address']['addressLocality'])
        self.assertNotIn('"@type": "LocalBusiness"', body)

    def test_home_page_uses_admin_title_and_description(self):
        body = self.client.get(reverse('index')).content.decode()

        self.assertIn('<title>Tally &amp; Software Solutions in Noida | INITIATOR SOLUTIONS</title>', body)
        self.assertIn(self.site_seo.default_description, body)

    def test_rich_text_h1_is_shown_as_h2_with_same_style(self):
        body = self.client.get(self.product.get_absolute_url()).content.decode()

        self.assertIn('<h2 data-rich-h1>Buy TallyPrime</h2>', body)
        self.assertIn('h2[data-rich-h1]', body)

    def test_automatic_description_is_clean_text(self):
        self.assertEqual(self.service.seo_description(), 'Tally Prime')
        long_text = plain_text_summary('<p>' + 'accounting software ' * 30 + '</p>')
        self.assertLessEqual(len(long_text), 155)
        self.assertTrue(long_text.endswith('…'))

    def test_schema_json_cannot_close_script_tag(self):
        self.service.meta_description = 'Bad </script><script>alert(1)</script>'
        self.service.save()

        body = self.client.get(self.service.get_absolute_url()).content.decode()
        schema = re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S)
        self.assertTrue(all(json.loads(block) for block in schema))

    def test_old_blog_id_url_redirects_to_slug_url(self):
        response = self.client.get(reverse('blog_single', kwargs={'id': self.blog.id}))

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], self.blog.get_absolute_url())

    def test_favicon_ico_redirects_to_png(self):
        response = self.client.get('/favicon.ico')

        self.assertEqual(response.status_code, 301)
        self.assertTrue(response['Location'].endswith('InitiatorLogo-favicon-96x96.png'))

    def test_llms_txt_lists_pages_as_markdown_links(self):
        body = self.client.get(reverse('llms_txt')).content.decode()

        self.assertTrue(body.startswith('# INITIATOR SOLUTIONS\n\n> '))
        self.assertIn(f'## Products\n- [Tally Prime](https://www.example.com{self.product.get_absolute_url()})', body)
        self.assertIn(f'- [Tally Prime](https://www.example.com{self.service.get_absolute_url()}): Tally Prime', body)
        self.assertIn('## Blog', body)
        self.assertIn('- Opening hours: Mo-Fr 10:00-18:30', body)

    def test_sitemap_uses_content_lastmod_and_skips_canonicalized_pages(self):
        self.blog.canonical_url = 'https://other.example.org/original-post/'
        self.blog.save()
        body = self.client.get(reverse('sitemap_xml')).content.decode()

        self.assertNotIn('migrate-tally-data', body)
        product_page = re.search(r'<loc>https://www.example.com/web2/web_product</loc><lastmod>([^<]+)</lastmod>', body)
        self.assertEqual(product_page.group(1), self.product.update_time.date().isoformat())

    def test_admin_shows_image_size_and_seo_hints(self):
        User.objects.create_superuser(username='admin', password='pass', email='admin@example.com')
        self.client.login(username='admin', password='pass')

        product_form = self.client.get(reverse('admin:web2_product_add')).content.decode()
        seo_form = self.client.get(reverse('admin:web2_siteseo_change', args=[self.site_seo.pk])).content.decode()
        self.assertIn('1200 x 800 px', product_form)
        self.assertIn('50-60 characters', product_form)
        self.assertIn('1200 x 630 px', seo_form)
        self.assertIn('IndexNow', seo_form)


class IndexNowTests(TestCase):
    def setUp(self):
        SiteSEO.objects.all().delete()
        self.site_seo = SiteSEO.objects.create(site_domain='https://www.example.com', indexnow_enabled=True)
        self.user = User.objects.create_user(username='indexnow', password='pass')

    def create_product(self):
        return Product.objects.create(
            user=self.user, product_group=group(CatalogGroup.TYPE_PRODUCT, Product.GROUP_TALLY), name='Tally Prime',
        )

    def test_key_is_generated_and_served(self):
        key = self.site_seo.indexnow_key

        self.assertRegex(key, r'^[0-9a-f]{32}$')
        response = self.client.get(f'/{key}.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), key)
        self.assertEqual(self.client.get(f'/{"0" * 32}.txt').status_code, 404)

    def test_key_file_is_hidden_when_disabled(self):
        key = self.site_seo.indexnow_key
        SiteSEO.objects.update(indexnow_enabled=False)

        self.assertEqual(self.client.get(f'/{key}.txt').status_code, 404)

    def test_saving_a_page_pings_indexnow_after_commit(self):
        with mock.patch('web2.indexnow._dispatch') as dispatch, self.captureOnCommitCallbacks(execute=True):
            product = self.create_product()

        site_seo_id, payload = dispatch.call_args.args
        self.assertEqual(site_seo_id, self.site_seo.pk)
        self.assertEqual(payload['host'], 'www.example.com')
        self.assertEqual(payload['keyLocation'], f'https://www.example.com/{self.site_seo.indexnow_key}.txt')
        self.assertEqual(payload['urlList'], [f'https://www.example.com{product.get_absolute_url()}'])

    def test_no_ping_when_disabled_or_in_debug(self):
        with mock.patch('web2.indexnow._dispatch') as dispatch:
            with override_settings(DEBUG=True), self.captureOnCommitCallbacks(execute=True):
                self.create_product()
            SiteSEO.objects.update(indexnow_enabled=False)
            with self.captureOnCommitCallbacks(execute=True):
                self.create_product()

        dispatch.assert_not_called()

    def test_send_records_status_and_never_raises(self):
        payload = {'urlList': ['https://www.example.com/x/']}
        response = mock.MagicMock(status=202)
        response.__enter__.return_value = response
        with mock.patch('web2.indexnow.urlrequest.urlopen', return_value=response):
            indexnow._send(self.site_seo.pk, payload)
        self.assertIn('OK: HTTP 202', SiteSEO.objects.get().indexnow_last_status)

        with mock.patch('web2.indexnow.urlrequest.urlopen', side_effect=OSError('offline')):
            indexnow._send(self.site_seo.pk, payload)
        self.assertIn('Failed: offline', SiteSEO.objects.get().indexnow_last_status)


class ApplySEOContentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='owner', password='pass', email='owner@example.com')
        self.cloud_group = group(CatalogGroup.TYPE_SERVICE, Service.GROUP_TALLY_CLOUD)

    def run_command(self, *args):
        out = StringIO()
        call_command('apply_seo_content', *args, stdout=out)
        return out.getvalue()

    def test_creates_all_pages_with_doc_titles_and_brand(self):
        self.run_command()

        site_seo = SiteSEO.objects.get()
        self.assertEqual(site_seo.organization_name, 'Initiator Solutions')
        self.assertEqual(site_seo.default_title, 'TallyPrime & Zoho Services in Noida | Initiator Solutions')
        self.assertEqual(Service.objects.count(), 9)
        self.assertEqual(Product.objects.get(slug='tallyprime').meta_title, 'TallyPrime Sales, Setup & Renewal in Noida')
        for page in seo_content.PAGES:
            self.assertLessEqual(len(page['meta_title']), 60, page['key'])
            self.assertLessEqual(len(page['meta_description']), 155, page['key'])
            self.assertNotIn('Initiator Solution ', page['meta_description'] + page['answer_summary'] + page['description'])

    def test_links_between_pages_are_resolved(self):
        self.run_command()

        for item in list(Service.objects.all()) + list(Product.objects.all()):
            self.assertNotIn('{link:', item.description)
            for url in re.findall(r'href="([^"]+)"', item.description):
                self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_existing_page_keeps_url_and_real_content(self):
        long_content = '<p>' + 'Our real Tally on Cloud content written in admin. ' * 20 + '</p>'
        existing = Service.objects.create(
            user=self.user, service_group=self.cloud_group, name='Tally On Cloud', slug='tally-on-cloud',
            description=long_content,
        )
        old_url = existing.get_absolute_url()

        self.run_command()

        existing.refresh_from_db()
        self.assertEqual(existing.get_absolute_url(), old_url)
        self.assertEqual(existing.description, long_content)
        self.assertEqual(existing.meta_title, 'Tally on Cloud in Noida - Access Tally Anywhere')
        self.assertEqual(Service.objects.filter(name='Tally on Cloud').count(), 1)

    def test_second_run_changes_nothing_and_dry_run_saves_nothing(self):
        dry = self.run_command('--dry-run')
        self.assertIn('Dry run', dry)
        self.assertEqual(Service.objects.count(), 0)

        self.run_command()
        second = self.run_command()
        self.assertNotIn('created', second)
        self.assertNotIn('updated', second)

    def test_service_page_has_visible_faqs_and_faq_schema(self):
        self.run_command()
        service = Service.objects.get(slug='tallyprime-customization')

        body = self.client.get(service.get_absolute_url()).content.decode()
        self.assertIn('<h3>Can TallyPrime be customized?</h3>', body)
        faq = next(
            json.loads(block) for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S)
            if '"FAQPage"' in block
        )
        self.assertEqual(len(faq['mainEntity']), 5)
        self.assertEqual(faq['mainEntity'][0]['name'], 'Can TallyPrime be customized?')

    def test_home_hero_types_slogan_and_contact_lists_areas_served(self):
        self.run_command()
        Lan_PageBanModel.objects.create(user=self.user)

        home = self.client.get(reverse('index')).content.decode()
        contact = self.client.get(reverse('contact')).content.decode()
        self.assertIn("data-typing>Let's Initiate Your Business With", home)
        self.assertIn('Noida-based software company for TallyPrime customization', home)
        self.assertIn('Areas Served', contact)
        self.assertIn('Greater Noida, Ghaziabad', contact)
        self.assertIn('<title>Contact Initiator Solutions - Sector 2, Noida</title>', contact)


class DeploySafetyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='owner', password='pass', email='owner@example.com')

    def test_check_site_data_passes_on_healthy_data(self):
        Lan_PageBanModel.objects.create(user=self.user)
        call_command('apply_seo_content', stdout=StringIO())
        out = StringIO()

        call_command('check_site_data', stdout=out)

        self.assertIn('Site data check passed: 0 error(s)', out.getvalue())

    def test_check_site_data_fails_when_a_page_crashes(self):
        Lan_PageBanModel.objects.create(user=self.user)
        product = Product.objects.create(user=self.user, product_group=group(CatalogGroup.TYPE_PRODUCT, Product.GROUP_TALLY), name='X')
        out = StringIO()

        with mock.patch('web2.views.render', side_effect=ValueError('broken template')):
            with self.assertRaises(CommandError):
                call_command('check_site_data', stdout=out)
        self.assertIn('crashes: ValueError: broken template', out.getvalue())
        self.assertIn(product.get_absolute_url(), out.getvalue())

    def test_check_site_data_checks_upload_folders_and_disk_space(self):
        Lan_PageBanModel.objects.create(user=self.user)
        out = StringIO()

        call_command('check_site_data', stdout=out)

        for line in ('Upload folder web2/product/ writable', 'Upload folder web2/landingpage/ writable',
                     'Upload folder _optimized/ writable', 'Upload temp folder writable', 'MB free disk space'):
            self.assertIn(line, out.getvalue())

    def test_check_site_data_fails_when_an_upload_folder_is_not_writable(self):
        Lan_PageBanModel.objects.create(user=self.user)
        real_temp_file = tempfile.NamedTemporaryFile

        def temp_file(*args, **kwargs):
            if 'product' in kwargs.get('dir', ''):
                raise PermissionError(13, 'Permission denied')
            return real_temp_file(*args, **kwargs)

        out = StringIO()
        with mock.patch('web2.management.commands.check_site_data.tempfile.NamedTemporaryFile', side_effect=temp_file):
            with self.assertRaises(CommandError):
                call_command('check_site_data', stdout=out)

        self.assertIn('Upload folder web2/product/ is not writable', out.getvalue())
        self.assertIn('Permission denied', out.getvalue())
        self.assertIn('sudo chown -R', out.getvalue())

    def test_check_site_data_fails_when_disk_is_almost_full(self):
        Lan_PageBanModel.objects.create(user=self.user)
        out = StringIO()

        with mock.patch('web2.management.commands.check_site_data.shutil.disk_usage', return_value=mock.Mock(free=100 * 1024 * 1024)):
            with self.assertRaises(CommandError):
                call_command('check_site_data', stdout=out)

        self.assertIn('Only 100 MB free disk space', out.getvalue())

    def test_check_site_data_reports_missing_home_banner(self):
        out = StringIO()

        with self.assertRaises(CommandError):
            call_command('check_site_data', stdout=out)
        self.assertIn('No home banner record', out.getvalue())

    @override_settings(DEBUG=False, ALLOWED_HOSTS=['testserver'])
    def test_error_page_falls_back_to_plain_html_when_rendering_fails(self):
        request = RequestFactory().get('/broken/')

        with mock.patch('web2.views.render', side_effect=RuntimeError('database down')):
            response = views.custom_500(request)

        self.assertEqual(response.status_code, 500)
        self.assertIn('Server error', response.content.decode())
        self.assertIn('Diagnostic ID', response.content.decode())


class FloatingContactTests(TestCase):
    def test_every_page_has_whatsapp_and_call_buttons_from_site_phone(self):
        SiteSEO.objects.all().delete()
        SiteSEO.objects.create(phone='+91 88825 95800')

        for url in (reverse('index'), reverse('contact'), reverse('web_dev')):
            body = self.client.get(url).content.decode()
            with self.subTest(url=url):
                self.assertIn('class="floating-contact"', body)
                self.assertIn('href="https://wa.me/918882595800?text=', body)
                self.assertIn('href="tel:+918882595800"', body)

    def test_phone_digits_adds_india_code(self):
        from web2.templatetags.seo_tags import phone_digits

        self.assertEqual(phone_digits('+91 88825 95800'), '918882595800')
        self.assertEqual(phone_digits('8882595800'), '918882595800')
        self.assertEqual(phone_digits('08882595800'), '918882595800')
        self.assertEqual(phone_digits(''), '')


class AdminStaticTests(TestCase):
    def test_admin_pages_only_reference_existing_static_files(self):
        # Guards against an old copy of admin static files in STATICFILES_DIRS
        # shadowing the files that match the installed Django version.
        User.objects.create_superuser(username='admin', password='pass', email='admin@example.com')
        self.client.login(username='admin', password='pass')

        for url_name in ['admin:index', 'admin:web2_product_add', 'admin:web2_service_changelist']:
            body = self.client.get(reverse(url_name)).content.decode()
            assets = re.findall(r'(?:href|src)="/static/([^"?]+)', body)
            self.assertIn('admin/css/base.css', assets)
            for asset in assets:
                self.assertTrue(finders.find(asset), f'{url_name} references missing static file {asset}')

        admin_css = finders.find('admin/css/base.css')
        self.assertNotIn(str(Path(settings.BASE_DIR) / 'static'), admin_css)


class ContactEmailTests(TestCase):
    def test_full_enquiry_sends_email(self):
        response = self.client.post(reverse('contact_email'), {
            'name': 'Asha',
            'cmpname': 'Asha Traders',
            'mob': '9999999999',
            'email': 'asha@example.com',
            'subject': 'Tally help',
            'message': 'Need invoice customization.',
        })

        self.assertRedirects(response, reverse('contact'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Tally help')
        self.assertIn('Asha Traders', mail.outbox[0].body)

    def test_missing_fields_do_not_crash(self):
        response = self.client.post(reverse('contact_email'), {'email': 'bot@example.com'})

        self.assertRedirects(response, reverse('contact'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'New Website Enquiry')

    def test_subject_with_line_break_does_not_crash(self):
        response = self.client.post(reverse('contact_email'), {
            'subject': 'Hello\nBcc: spam@example.com',
        })

        self.assertRedirects(response, reverse('contact'))
        self.assertEqual(mail.outbox[0].subject, 'Hello Bcc: spam@example.com')

    def test_email_failure_still_forwards_to_crm(self):
        with mock.patch('web2.views.send_mail', side_effect=SMTPException('down')), \
                mock.patch('web2.views._forward_contact_to_crm') as forward:
            response = self.client.post(reverse('contact_email'), {'name': 'Asha'})

        self.assertRedirects(response, reverse('contact'))
        forward.assert_called_once()
        self.assertEqual(forward.call_args.args[1]['name'], 'Asha')


class NewsLetterTests(TestCase):
    def subscribe(self, email):
        return self.client.post(reverse('news_letter'), {'name': email})

    def test_valid_email_is_saved_lowercase(self):
        response = self.subscribe('  Asha@Example.com ')

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(list(OurNewsLetter.objects.values_list('name', flat=True)), ['asha@example.com'])

    def test_blank_and_invalid_emails_are_ignored(self):
        for email in ['', '   ', 'not-an-email', 'a@b']:
            self.assertRedirects(self.subscribe(email), reverse('index'))

        self.assertEqual(OurNewsLetter.objects.count(), 0)

    def test_duplicate_email_is_saved_once(self):
        self.subscribe('asha@example.com')
        self.subscribe('ASHA@example.com')

        self.assertEqual(OurNewsLetter.objects.count(), 1)

    def test_email_longer_than_field_is_ignored(self):
        self.subscribe(f'{"a" * 60}@{"b" * 140}.com')

        self.assertEqual(OurNewsLetter.objects.count(), 0)


class OptimizedImageTests(TestCase):
    def setUp(self):
        from PIL import Image

        self.media_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=self.media_root)
        override.enable()
        self.addCleanup(override.disable)
        self.name = 'web2/landingpage/hero.png'
        Path(self.media_root, 'web2/landingpage').mkdir(parents=True)
        Image.new('RGBA', (2400, 1600), (65, 84, 241, 128)).save(Path(self.media_root, self.name))
        self.user = User.objects.create_user(username='img-user', password='pass')

    def test_home_hero_and_cards_use_small_webp_copies(self):
        Lan_PageBanModel.objects.create(user=self.user, img=self.name)
        Product.objects.create(
            user=self.user, product_group=group(CatalogGroup.TYPE_PRODUCT, Product.GROUP_TALLY),
            name='Tally Prime', img=self.name, show_on_landing=True,
        )

        body = self.client.get(reverse('index')).content.decode()

        self.assertIn(f'src="/web2/img/1200/{self.name}"', body)
        self.assertIn(f'src="/web2/img/800/{self.name}"', body)
        self.assertNotIn(f'src="{settings.MEDIA_URL}{self.name}"', body)

    def test_copy_is_resized_webp_with_transparency_and_cached(self):
        from PIL import Image

        response = self.client.get(f'/web2/img/800/{self.name}')
        content = b''.join(response.streaming_content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/webp')
        self.assertIn('max-age=2592000', response['Cache-Control'])
        with Image.open(BytesIO(content)) as image:
            self.assertEqual((image.format, image.size, image.mode), ('WEBP', (800, 533), 'RGBA'))

        again = self.client.get(f'/web2/img/800/{self.name}', HTTP_IF_MODIFIED_SINCE=response['Last-Modified'])
        self.assertEqual(again.status_code, 304)

    def test_bad_requests_return_404(self):
        for url in (
            f'/web2/img/999/{self.name}',            # width not allowed
            '/web2/img/800/web2/landingpage/missing.png',
            '/web2/img/800/../../../etc/passwd.png',
            '/web2/img/800/web2/landingpage/logo.svg',
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_unconvertible_image_falls_back_to_original(self):
        Path(self.media_root, 'web2/landingpage/broken.png').write_bytes(b'not an image')

        response = self.client.get('/web2/img/800/web2/landingpage/broken.png')

        self.assertRedirects(response, f'{settings.MEDIA_URL}web2/landingpage/broken.png', fetch_redirect_response=False)

    def test_filter_keeps_original_url_for_svg_and_blank(self):
        from web2.templatetags.image_tags import image_url

        self.assertEqual(image_url(Lan_PageBanModel(img='web2/landingpage/logo.svg').img, 800), f'{settings.MEDIA_URL}web2/landingpage/logo.svg')
        self.assertEqual(image_url(Lan_PageBanModel().img, 800), '')

    def test_admin_product_image_upload_saves_file(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image

        admin_user = User.objects.create_superuser(username='uploader', password='pass', email='u@example.com')
        self.client.login(username='uploader', password='pass')
        product = Product.objects.create(
            user=admin_user, product_group=group(CatalogGroup.TYPE_PRODUCT, Product.GROUP_TALLY), name='Tally Prime',
        )
        def upload(file_name):
            buffer = BytesIO()
            Image.new('RGB', (1600, 900), (1, 41, 112)).save(buffer, 'PNG')
            return self.client.post(reverse('admin:web2_product_change', args=[product.pk]), {
                'user': admin_user.pk,
                'product_group': product.product_group_id,
                'name': 'Tally Prime',
                'slug': product.slug,
                'sort_order': 0,
                'show_in_catalog': 'on',
                'is_published': 'on',
                'allow_index': 'on',
                'img': SimpleUploadedFile(file_name, buffer.getvalue(), content_type='image/png'),
                '_save': 'Save',
            })

        response = upload('banner.png')

        self.assertEqual(response.status_code, 302)
        product.refresh_from_db()
        self.assertEqual(product.img.name, 'web2/product/banner.png')
        self.assertTrue(Path(self.media_root, product.img.name).exists())

        # A file name over the 100-character field limit is a form message, not a crash.
        response = upload(f'{"very_long_image_name_" * 6}.png')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ensure this filename has at most 100 characters')

    def test_admin_upload_limit_is_10_mb_on_every_image_form(self):
        from django.contrib import admin as django_admin
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image

        from .models import PortfolioModel

        def png_of_size(size):
            buffer = BytesIO()
            Image.new('RGB', (50, 50)).save(buffer, 'PNG')
            # Trailing bytes after the PNG end marker keep it a valid image.
            return buffer.getvalue() + b'\0' * (size - buffer.tell())

        request = RequestFactory().get('/admin/')
        request.user = User.objects.create_superuser(username='limit', password='pass', email='l@example.com')
        for model, field in ((Product, 'img'), (Blog, 'image'), (Lan_PageBanModel, 'img'), (PortfolioModel, 'img')):
            form_class = django_admin.site._registry[model].get_form(request)
            for size, allowed in ((10 * 1024 * 1024 - 1024, True), (10 * 1024 * 1024 + 1024, False)):
                with self.subTest(model=model.__name__, size=size):
                    upload = SimpleUploadedFile('photo.png', png_of_size(size), content_type='image/png')
                    form = form_class(data={}, files={field: upload})
                    form.is_valid()
                    errors = ' '.join(form.errors.get(field, []))
                    self.assertEqual('the limit is 10 MB' not in errors, allowed, errors)

    def test_optimize_images_command_creates_all_sizes(self):
        Lan_PageBanModel.objects.create(user=self.user, img=self.name)
        out = StringIO()

        call_command('optimize_images', stdout=out)

        self.assertIn('3 image copies ready, 0 skipped.', out.getvalue())
        for width in (400, 800, 1200):
            self.assertTrue(Path(self.media_root, '_optimized', str(width), f'{self.name}.webp').exists())
