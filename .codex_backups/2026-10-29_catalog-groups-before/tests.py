from pathlib import Path
from smtplib import SMTPException
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from . import views
from .models import Blog, OurNewsLetter, Product, ProductUpload, Service, SiteSEO


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
            product_group=Product.GROUP_TALLY,
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
            service_group=Service.GROUP_WEB_DEVELOPMENT,
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
            service_group=Service.GROUP_TALLY_VERTICAL,
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

    def test_static_502_page_exists_for_nginx_gateway_errors(self):
        error_page = Path(settings.BASE_DIR) / 'static' / 'error_pages' / '502.html'

        self.assertTrue(error_page.exists())
        body = error_page.read_text(encoding='utf-8')
        self.assertIn('502', body)
        self.assertIn('Bad Gateway', body)
        self.assertIn('nginx', body)


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
