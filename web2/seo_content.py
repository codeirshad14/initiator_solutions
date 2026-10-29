"""SEO content for initiatorsolutions.com (from "Initiator Solution SEO Points", Oct 2026).

Applied by: python manage.py apply_seo_content
Facts confirmed by the owner: brand "Initiator Solutions", 7+ years Tally
customization experience, Tally on Cloud daily backups, Tally course
certificate, classroom (Sector 2, Noida) and online batches.
Not known yet, so deliberately left out: prices, course fee / duration /
batch timings, Tally App sync details, Tally AI data-privacy details.

In descriptions, {link:<key>} is replaced with the URL of that page.
"""

BRAND = 'Initiator Solutions'

ONE_LINE_DESCRIPTION = (
    'Initiator Solutions is a Noida-based software company that provides TallyPrime customization, '
    'Tally integration, Tally on Cloud, Tally AI, Tally training, Zoho Books and Zoho services, '
    'and web application development.'
)

SITE_SEO = {
    'site_name': BRAND,
    'organization_name': BRAND,
    'default_title': 'TallyPrime & Zoho Services in Noida | Initiator Solutions',
    'default_description': (
        'TallyPrime customization, integration, Tally on Cloud, Tally AI, Zoho Books and web development. '
        'Noida Sector 2, serving all India.'
    ),
    'default_keywords': (
        'TallyPrime Noida, TallyPrime customization, Tally integration, Tally on Cloud, Tally AI, Tally mobile app, '
        'Tally course Noida, Zoho Books Noida, Zoho consultant, web development company Noida, Initiator Solutions'
    ),
    'ai_answer_summary': ONE_LINE_DESCRIPTION,
    'service_area': 'Noida, Greater Noida, Ghaziabad, Delhi, Gurugram, All India (remote)',
}

# New service groups (existing groups are reused by slug).
SERVICE_GROUPS = [
    ('tally-customization-integration', 'Tally Customization & Integration', 50),
    ('tally-app-ai', 'Tally App & Tally AI', 52),
    ('tally-on-cloud', 'Tally On Cloud', 70),
    ('tally-training', 'Tally Course & Training', 72),
    ('zoho-services', 'Zoho Books & Zoho Services', 74),
    ('website-development', 'Website Development', 10),
]


def _faq(items):
    parts = ['<h2>Frequently asked questions</h2>']
    for question, answer in items:
        parts.append(f'<h3>{question}</h3><p>{answer}</p>')
    return ''.join(parts)


def _related(links):
    items = ''.join(f'<li><a href="{{link:{key}}}">{label}</a></li>' for key, label in links)
    return f'<h2>Related services</h2><ul>{items}</ul>'


# Each page: kind (product/service), group slug, slug, names to match an
# existing record, H1 name, SEO fields, card text and full page content.
PAGES = [
    {
        'key': 'tallyprime',
        'kind': 'product',
        'group': 'tally-prime',
        'match_slugs': ['tallyprime', 'tally-prime'],
        'match_names': ['Tally Prime', 'TallyPrime'],
        'name': 'TallyPrime Sales, Setup and Renewal',
        'meta_title': 'TallyPrime Sales, Setup & Renewal in Noida',
        'meta_description': 'Buy, install and renew TallyPrime with expert setup, data migration and support. Office in Noida Sector 2.',
        'focus_keyword': 'TallyPrime Noida',
        'answer_summary': (
            'Initiator Solutions sells, installs and renews TallyPrime Silver and Gold for businesses in Noida and across India, '
            'with setup, data migration and ongoing support from our office in Sector 2, Noida.'
        ),
        'short_description': 'Buy, install and renew TallyPrime Silver or Gold with expert setup, data migration and support from our Noida Sector 2 office.',
        'description': (
            '<p>Initiator Solutions sells, installs and renews TallyPrime for businesses in Noida, Delhi NCR and across India. '
            'We handle the licence, installation, company setup, data migration and support, so your team can start billing on day one.</p>'
            '<h2>Who it is for</h2>'
            '<p>Traders, distributors, manufacturers, service companies and CAs who want genuine TallyPrime with local setup and support.</p>'
            '<h2>What you get</h2>'
            '<ul><li>Genuine TallyPrime Silver or Gold licence</li><li>Installation and company creation</li>'
            '<li>GST, ledgers, stock items and voucher setup</li><li>Data migration from older Tally versions</li>'
            '<li>TSS renewal and upgrade help</li><li>Support by phone, WhatsApp and remote session</li></ul>'
            '<h2>How it works</h2>'
            '<ol><li>Tell us how many users and branches you have.</li><li>We suggest Silver or Gold and share the current price.</li>'
            '<li>We install, set up and migrate your data.</li><li>We train your team and stay available for support.</li></ol>'
            + _faq([
                ('What is the TallyPrime price?',
                 'TallyPrime is sold at the official prices set by Tally Solutions. Silver and Gold have different prices, and prices are revised '
                 'from time to time. Call or WhatsApp us for today\'s price and a quote that includes installation and setup.'),
                ('How do I renew TallyPrime (TSS)?',
                 'TSS (Tally Software Services) is the yearly renewal that keeps TallyPrime updated with new releases and statutory changes such as GST, '
                 'and keeps connected services like remote access working. Share your Tally serial number and we renew it for you online.'),
                ('Silver vs Gold: which do I need?',
                 'Silver is a single-user licence for one computer. Gold is a multi-user licence for unlimited users on the same local network. '
                 'If more than one person needs to work in Tally at the same time, choose Gold.'),
            ])
            + _related([
                ('tallyprime-customization', 'TallyPrime Customization'),
                ('tally-on-cloud', 'Tally on Cloud'),
                ('tally-course-noida', 'TallyPrime Course in Noida'),
            ])
        ),
    },
    {
        'key': 'tallyprime-customization',
        'kind': 'service',
        'group': 'tally-customization-integration',
        'match_slugs': ['tallyprime-customization', 'tally-customization'],
        'match_names': ['Tally Customization', 'TallyPrime Customization', 'TallyPrime Customization Services'],
        'name': 'TallyPrime Customization Services',
        'meta_title': 'TallyPrime Customization Services | TDL Experts',
        'meta_description': 'Custom reports, invoice formats, fields and automation in TallyPrime using TDL. 7+ years of Tally customization experience.',
        'focus_keyword': 'TallyPrime customization',
        'answer_summary': (
            'TallyPrime customization means changing Tally with TDL (Tally Definition Language) to add custom reports, invoice formats, '
            'fields and automation. Initiator Solutions has 7+ years of Tally customization experience and serves businesses in Noida and across India.'
        ),
        'short_description': 'Custom reports, invoice formats, extra fields and automation in TallyPrime using TDL, by a team with 7+ years of Tally customization experience.',
        'description': (
            '<p>Initiator Solutions customizes TallyPrime with TDL so it fits the way your business works. '
            'We serve companies in Noida, Delhi NCR and across India, with 7+ years of Tally customization experience.</p>'
            '<h2>Who it is for</h2>'
            '<p>Businesses whose invoices, reports or approvals need more than standard TallyPrime offers: manufacturers, distributors, '
            'retailers, exporters and service companies.</p>'
            '<h2>What we customize</h2>'
            '<ul><li>Invoice, quotation and delivery note formats</li><li>Custom reports and MIS dashboards</li>'
            '<li>Extra fields on masters and vouchers</li><li>Approval, validation and locking rules</li>'
            '<li>Automation of repetitive entries</li><li>Industry modules such as barcode, garments and approval systems</li></ul>'
            '<h2>How it works</h2>'
            '<ol><li>Requirement call and sample formats</li><li>Written scope, quote and timeline</li>'
            '<li>Development and testing on a copy of your data</li><li>Installation, training and support</li></ol>'
            + _faq([
                ('Can TallyPrime be customized?',
                 'Yes. TallyPrime is built on TDL (Tally Definition Language), which lets developers add reports, fields, formats and rules '
                 'without changing your data. The customization is installed as a TDL file and can be switched on or off.'),
                ('What can be changed in TallyPrime?',
                 'Invoice and document formats, reports, extra fields on masters and vouchers, validations, approvals, automatic entries and '
                 'integrations with other software. If a requirement is about how Tally looks or behaves, it can usually be done with TDL.'),
                ('How much does Tally customization cost?',
                 'It depends on the work. A single invoice format is a small job, while a module with several reports and approvals is larger. '
                 'We share a written quote and timeline after a short requirement call.'),
                ('How long does Tally customization take?',
                 'Simple changes such as a new invoice layout or a few extra fields are quick. Larger modules are delivered in planned stages. '
                 'The exact timeline is part of your written quote.'),
                ('Will my customization work after a Tally update?',
                 'TDL customizations normally keep working across TallyPrime releases. After a major Tally release we recommend a quick test, '
                 'and we adjust the TDL if anything needs changing.'),
            ])
            + _related([
                ('tallyprime-integration', 'TallyPrime Integration'),
                ('tally-ai', 'AI for TallyPrime'),
                ('tallyprime', 'TallyPrime Sales and Renewal'),
            ])
        ),
    },
    {
        'key': 'tallyprime-integration',
        'kind': 'service',
        'group': 'tally-customization-integration',
        'match_slugs': ['tallyprime-integration', 'tally-integration'],
        'match_names': ['Tally Integration', 'TallyPrime Integration', 'TallyPrime Integration Services'],
        'name': 'TallyPrime Integration Services',
        'meta_title': 'TallyPrime Integration with Website, CRM & Apps',
        'meta_description': 'Connect TallyPrime with e-commerce, CRM, ERP and custom apps using XML/JSON APIs. Real-time sync, no manual entry.',
        'focus_keyword': 'TallyPrime integration',
        'answer_summary': (
            'TallyPrime integration connects Tally with websites, e-commerce stores, CRM, ERP and custom apps through Tally\'s XML/JSON interface, '
            'so orders, invoices, payments and stock sync automatically. Initiator Solutions builds these integrations for businesses in Noida and across India.'
        ),
        'short_description': 'Connect TallyPrime with your website, e-commerce store, CRM, ERP or custom app using XML/JSON APIs, with automatic sync and no manual entry.',
        'description': (
            '<p>Initiator Solutions connects TallyPrime with the other software your business uses, so data moves automatically instead of being typed twice. '
            'We build integrations for companies in Noida, Delhi NCR and across India.</p>'
            '<h2>Who it is for</h2>'
            '<p>Businesses that sell online, use a CRM or ERP, or run a custom app and want orders, invoices, payments and stock to reach Tally without manual entry.</p>'
            '<h2>What we connect</h2>'
            '<ul><li>E-commerce stores and marketplaces</li><li>CRM and sales apps</li><li>ERP, POS and billing software</li>'
            '<li>Payment gateways and banks</li><li>Custom web and mobile apps</li></ul>'
            '<h2>How it works</h2>'
            '<ol><li>Map which data moves where (orders, parties, items, payments)</li><li>Build and test the connection on a copy of your data</li>'
            '<li>Go live with logs and error alerts</li><li>Support and changes as your systems grow</li></ol>'
            + _faq([
                ('Can Tally connect to my website or e-commerce store?',
                 'Yes. Orders, customers, items and payments from your website or store can be created in TallyPrime automatically, '
                 'and stock or price updates can flow back. This removes double entry and typing mistakes.'),
                ('Does Tally have an API?',
                 'Yes. TallyPrime has a built-in integration interface: other software can read and write Tally data over HTTP using XML, '
                 'and JSON in recent TallyPrime releases. We use this interface to build safe, tested connections.'),
                ('Is the sync real-time?',
                 'It can be. Data can sync as each order or payment happens, or on a schedule, depending on your volume. '
                 'Tally must be running on a computer or on a Tally on Cloud server for the sync to work.'),
            ])
            + _related([
                ('tallyprime-customization', 'TallyPrime Customization'),
                ('tally-on-cloud', 'Tally on Cloud'),
                ('tally-mobile-app', 'Tally Mobile App'),
            ])
        ),
    },
    {
        'key': 'tally-mobile-app',
        'kind': 'service',
        'group': 'tally-app-ai',
        'match_slugs': ['tally-mobile-app', 'tally-app'],
        'match_names': ['Tally Mobile App', 'Tally App'],
        'name': 'Tally Mobile App',
        'meta_title': 'Tally Mobile App - View Tally Reports on Phone',
        'meta_description': 'See sales, outstanding, stock and ledgers from TallyPrime on your mobile. Secure, real-time Tally data anywhere.',
        'focus_keyword': 'Tally mobile app',
        'answer_summary': (
            'The Tally Mobile App by Initiator Solutions shows sales, outstanding, stock and ledgers from TallyPrime on your phone, '
            'so owners and sales teams can check business numbers anywhere in India.'
        ),
        'short_description': 'See sales, outstanding, stock and ledgers from TallyPrime on your mobile phone, anywhere.',
        'description': (
            '<p>The Tally Mobile App from Initiator Solutions puts your TallyPrime reports on your phone. '
            'Business owners and sales teams in Noida and across India use it to check sales, outstanding, stock and ledgers away from the office.</p>'
            '<h2>Who it is for</h2>'
            '<p>Owners, managers and field sales teams who need Tally numbers on the move without opening Tally on a computer.</p>'
            '<h2>What you can see</h2>'
            '<ul><li>Sales and purchase summaries</li><li>Customer and supplier outstanding</li><li>Stock and item details</li><li>Ledgers and statements</li></ul>'
            + _faq([
                ('Can I see Tally reports on mobile?',
                 'Yes. The app shows sales, outstanding, stock and ledgers from your TallyPrime company on your phone, '
                 'so you can check numbers and follow up on payments from anywhere.'),
                ('Is my Tally data safe on the app?',
                 'Access needs a login, and we set it up so only your team can see your company data. '
                 'We walk you through how the data is synced and stored before you start.'),
            ])
            + _related([
                ('tally-ai', 'AI for TallyPrime'),
                ('tally-on-cloud', 'Tally on Cloud'),
                ('tallyprime-integration', 'TallyPrime Integration'),
            ])
        ),
    },
    {
        'key': 'tally-ai',
        'kind': 'service',
        'group': 'tally-app-ai',
        'match_slugs': ['tally-ai'],
        'match_names': ['Tally AI', 'AI for TallyPrime'],
        'name': 'AI for TallyPrime',
        'meta_title': 'Tally AI - AI Reports & Automation for TallyPrime',
        'meta_description': 'Ask questions to your Tally data in plain language. AI reports, insights and automation for TallyPrime users.',
        'focus_keyword': 'Tally AI',
        'answer_summary': (
            'Tally AI by Initiator Solutions lets TallyPrime users ask questions about their accounting data in plain language '
            'and get AI reports, insights and automation, without building reports by hand.'
        ),
        'short_description': 'Ask questions to your Tally data in plain language and get AI reports, insights and automation for TallyPrime.',
        'description': (
            '<p>Tally AI from Initiator Solutions lets you ask questions about your TallyPrime data in plain language and get answers, reports and insights. '
            'It is built for TallyPrime users in Noida and across India who want answers without building reports by hand.</p>'
            '<h2>Who it is for</h2>'
            '<p>Owners, accountants and managers who use TallyPrime and want faster answers about sales, payments and stock.</p>'
            '<h2>What it does</h2>'
            '<ul><li>Answers questions about your Tally data in plain language</li><li>Creates AI reports and summaries</li>'
            '<li>Highlights trends and insights</li><li>Automates repetitive reporting</li></ul>'
            + _faq([
                ('How can AI be used with Tally data?',
                 'Instead of opening many reports, you type a question such as "Which customers are overdue?" or "How did sales change this month?" '
                 'and Tally AI answers from your TallyPrime data in plain language.'),
                ('What reports can Tally AI create?',
                 'Reports such as sales trends, top customers and items, outstanding and overdue payments, stock movement and period comparisons, '
                 'based on the data in your TallyPrime company.'),
            ])
            + _related([
                ('tally-mobile-app', 'Tally Mobile App'),
                ('tallyprime-customization', 'TallyPrime Customization'),
                ('tallyprime-integration', 'TallyPrime Integration'),
            ])
        ),
    },
    {
        'key': 'tally-on-cloud',
        'kind': 'service',
        'group': 'tally-on-cloud',
        'match_slugs': ['tally-on-cloud'],
        'match_names': ['Tally On Cloud', 'Tally on Cloud'],
        'name': 'Tally on Cloud',
        'meta_title': 'Tally on Cloud in Noida - Access Tally Anywhere',
        'meta_description': 'Run TallyPrime on a secure cloud server. Multi-user access from anywhere, daily backups. Plans for small businesses.',
        'focus_keyword': 'Tally on Cloud Noida',
        'answer_summary': (
            'Tally on Cloud runs TallyPrime on a secure cloud server, so your team can work in Tally from any location with daily backups. '
            'Initiator Solutions sets it up for businesses in Noida and across India.'
        ),
        'short_description': 'Run TallyPrime on a secure cloud server with multi-user access from anywhere and daily backups.',
        'description': (
            '<p>Initiator Solutions runs your TallyPrime on a secure cloud server, so your team can work in Tally from the office, home or another city. '
            'We set up and support Tally on Cloud for businesses in Noida and across India, with daily backups.</p>'
            '<h2>Who it is for</h2>'
            '<p>Businesses with more than one branch, remote accountants or CAs, and owners who want to check Tally from anywhere.</p>'
            '<h2>What you get</h2>'
            '<ul><li>TallyPrime on a secure cloud server</li><li>Multi-user access from any location</li><li>Daily backups</li>'
            '<li>Setup, data migration and user creation</li><li>Support when you need it</li></ul>'
            + _faq([
                ('What is Tally on Cloud?',
                 'Tally on Cloud means your TallyPrime and its data run on a cloud server instead of an office computer. '
                 'Your team opens Tally through a secure remote connection from any computer, and the data stays in one place.'),
                ('What does Tally on Cloud cost per user per month?',
                 'Plans are priced per user per month and depend on the number of users and storage you need. '
                 'Contact us for the current plan list for small businesses.'),
                ('Is Tally on Cloud safe?',
                 'Yes. Your data runs on a secure cloud server, every user has their own login, and backups are taken daily, '
                 'so a lost or broken office computer does not mean lost accounts.'),
                ('Can multiple users work at the same time?',
                 'Yes. With a TallyPrime Gold licence, several users can work in the same company at the same time from different locations.'),
            ])
            + _related([
                ('tallyprime', 'TallyPrime Sales and Renewal'),
                ('tallyprime-integration', 'TallyPrime Integration'),
                ('tally-mobile-app', 'Tally Mobile App'),
            ])
        ),
    },
    {
        'key': 'tally-course-noida',
        'kind': 'service',
        'group': 'tally-training',
        'match_slugs': ['tally-course-noida', 'tally-course'],
        'match_names': ['Tally Course', 'TallyPrime Course in Noida'],
        'name': 'TallyPrime Course in Noida',
        'meta_title': 'Tally Course in Noida - TallyPrime with GST',
        'meta_description': 'Learn TallyPrime with GST, inventory and payroll. Classroom in Noida Sector 2 and online batches. Certificate included.',
        'focus_keyword': 'Tally course in Noida',
        'answer_summary': (
            'Initiator Solutions teaches TallyPrime with GST, inventory and payroll in classroom batches at Sector 2, Noida and in online batches, '
            'with a certificate on completion.'
        ),
        'short_description': 'Learn TallyPrime with GST, inventory and payroll. Classroom batches in Noida Sector 2 and online batches, with a certificate.',
        'description': (
            '<p>Initiator Solutions teaches TallyPrime with GST, inventory and payroll, in classroom batches at our Sector 2, Noida office and in online batches. '
            'Every student receives a certificate on completion.</p>'
            '<h2>Who it is for</h2>'
            '<p>Students, job seekers, accountants and business owners who want practical TallyPrime skills for accounting jobs or their own business.</p>'
            '<h2>What you will learn</h2>'
            '<ul><li>Company creation, ledgers and vouchers</li><li>GST setup, GST invoices and GST reports</li>'
            '<li>Inventory and stock management</li><li>Payroll</li><li>Day-to-day reports and year-end work</li></ul>'
            + _faq([
                ('Is GST included in the Tally course?',
                 'Yes. The course covers GST in TallyPrime, including GST setup, GST invoices and the GST reports used for filing returns.'),
                ('Do I get a certificate?',
                 'Yes. Every student who completes the TallyPrime course receives a certificate from Initiator Solutions.'),
                ('Is there an online Tally batch?',
                 'Yes. You can join a classroom batch at our office in Sector 2, Noida or an online batch from anywhere in India.'),
            ])
            + _related([
                ('tallyprime', 'TallyPrime Sales and Renewal'),
                ('zoho-books', 'Zoho Books Services'),
                ('tallyprime-customization', 'TallyPrime Customization'),
            ])
        ),
    },
    {
        'key': 'zoho-books',
        'kind': 'service',
        'group': 'zoho-services',
        'match_slugs': ['zoho-books-services', 'zoho-books-implementation'],
        'match_names': ['Zoho Books Services', 'Zoho Books Implementation'],
        'name': 'Zoho Books Services',
        'meta_title': 'Zoho Books Implementation in Noida | GST Setup',
        'meta_description': 'Zoho Books setup, GST and e-invoice configuration, Tally to Zoho migration and team training.',
        'focus_keyword': 'Zoho Books implementation Noida',
        'answer_summary': (
            'Initiator Solutions sets up Zoho Books for businesses in Noida and across India, including GST and e-invoice configuration, '
            'migration from Tally to Zoho Books and team training.'
        ),
        'short_description': 'Zoho Books setup, GST and e-invoice configuration, Tally to Zoho Books migration and team training.',
        'description': (
            '<p>Initiator Solutions implements Zoho Books for businesses in Noida and across India. '
            'We configure GST and e-invoicing, move your data from Tally and train your team.</p>'
            '<h2>Who it is for</h2>'
            '<p>Businesses moving to cloud accounting, and Tally users who want to switch to Zoho Books.</p>'
            '<h2>What you get</h2>'
            '<ul><li>Zoho Books organization setup</li><li>GST, e-invoice and e-way bill configuration</li>'
            '<li>Tally to Zoho Books data migration</li><li>Invoice templates and workflows</li><li>Team training and support</li></ul>'
            + _faq([
                ('How do I migrate from Tally to Zoho Books?',
                 'Export your masters and opening balances from Tally, map ledgers, taxes and items to Zoho Books, import them, '
                 'then check the trial balance against Tally before you start billing. We do this end to end for you.'),
                ('Zoho Books vs TallyPrime: which is better?',
                 'Zoho Books is cloud software you use in a browser on a subscription, and it links with other Zoho apps. '
                 'TallyPrime is installed software with a licence and yearly renewal, and is strong in inventory and offline work. '
                 'The right choice depends on how and where your team works.'),
                ('Does Zoho Books support GST e-invoice?',
                 'Yes. Zoho Books supports GST e-invoicing in India and can generate e-way bills. We configure both for your business.'),
            ])
            + _related([
                ('zoho-services', 'Zoho Implementation Services'),
                ('tallyprime', 'TallyPrime Sales and Renewal'),
                ('tally-course-noida', 'TallyPrime Course in Noida'),
            ])
        ),
    },
    {
        'key': 'zoho-services',
        'kind': 'service',
        'group': 'zoho-services',
        'match_slugs': ['zoho-services', 'zoho-implementation-services'],
        'match_names': ['Zoho Services', 'All Zoho Services', 'Zoho Implementation Services'],
        'name': 'Zoho Implementation Services',
        'meta_title': 'Zoho Consultant in Noida - CRM, Inventory, One',
        'meta_description': 'Implementation and customization of Zoho CRM, Inventory, People and Zoho One for growing businesses.',
        'focus_keyword': 'Zoho consultant Noida',
        'answer_summary': (
            'Initiator Solutions implements and customizes Zoho CRM, Zoho Inventory, Zoho People and Zoho One for growing businesses '
            'in Noida and across India.'
        ),
        'short_description': 'Implementation and customization of Zoho CRM, Zoho Inventory, Zoho People and Zoho One for growing businesses.',
        'description': (
            '<p>Initiator Solutions implements and customizes Zoho apps for growing businesses in Noida and across India. '
            'We set up Zoho CRM, Inventory, People and Zoho One and connect them with your accounting.</p>'
            '<h2>Who it is for</h2>'
            '<p>Small and mid-size businesses that want sales, stock, HR and accounts in one connected system.</p>'
            '<h2>What we implement</h2>'
            '<ul><li>Zoho CRM</li><li>Zoho Inventory</li><li>Zoho People</li><li>Zoho One</li><li>Integration with Zoho Books or TallyPrime</li></ul>'
            + _faq([
                ('Which Zoho apps does a small business need?',
                 'Most small businesses start with Zoho Books for accounts and Zoho CRM for sales, then add Zoho Inventory for stock '
                 'and Zoho People for HR as they grow. We suggest the right set after understanding your work.'),
                ('What does Zoho One include?',
                 'Zoho One is a single licence that covers most Zoho apps, including CRM, Books, Inventory, People, Desk and Projects, '
                 'so all departments can work in one connected suite.'),
            ])
            + _related([
                ('zoho-books', 'Zoho Books Services'),
                ('web-development', 'Website and Web Application Development'),
                ('tallyprime-integration', 'TallyPrime Integration'),
            ])
        ),
    },
    {
        'key': 'web-development',
        'kind': 'service',
        'group': 'website-development',
        'match_slugs': ['web-development', 'website-development'],
        'match_names': ['Website Development', 'Website and Web Application Development'],
        'name': 'Website and Web Application Development',
        'meta_title': 'Website & Web App Development Company in Noida',
        'meta_description': 'Business websites and custom web applications built with Python and Django. SEO-ready, fast, mobile-friendly.',
        'focus_keyword': 'website development company Noida',
        'answer_summary': (
            'Initiator Solutions builds business websites and custom web applications with Python and Django for companies in Noida and across India. '
            'Every site is SEO-ready, fast and mobile-friendly.'
        ),
        'short_description': 'Business websites and custom web applications built with Python and Django. SEO-ready, fast and mobile-friendly.',
        'description': (
            '<p>Initiator Solutions builds business websites and custom web applications with Python and Django. '
            'We work with companies in Noida, Delhi NCR and across India, and every site is SEO-ready, fast and mobile-friendly.</p>'
            '<h2>Who it is for</h2>'
            '<p>Businesses that need a professional website, a customer or dealer portal, or a custom web app connected to Tally or Zoho.</p>'
            '<h2>What we build</h2>'
            '<ul><li>Business and company websites</li><li>Custom web applications and admin panels</li>'
            '<li>Customer, dealer and employee portals</li><li>Integrations with TallyPrime and Zoho</li></ul>'
            + _faq([
                ('How much does a business website cost in India?',
                 'It depends on the number of pages, features and integrations. A simple business website costs much less than a custom web application. '
                 'We share a written quote after a short requirement call.'),
                ('How long does a web application take?',
                 'A business website is the quickest. Custom web applications are built in planned stages, with a demo after each stage, '
                 'and the timeline is fixed in your quote.'),
                ('Will my website be SEO-friendly?',
                 'Yes. Every site we build has clean URLs, page titles and descriptions, a sitemap, structured data and fast mobile pages, '
                 'so Google can understand and rank it.'),
            ])
            + _related([
                ('tallyprime-integration', 'TallyPrime Integration'),
                ('zoho-services', 'Zoho Implementation Services'),
                ('tally-mobile-app', 'Tally Mobile App'),
            ])
        ),
    },
]
