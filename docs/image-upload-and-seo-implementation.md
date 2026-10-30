# Image Upload, Fallback, GUI, and SEO Implementation

Date: 2026-07-20

## Upload Size Policy

Update 2026-10-30: admin uploads are limited to **10 MB per file** by the admin
forms (`UploadSizeLimitForm` in `web2/admin.py`); a larger file shows a form
message instead of an error page. There is still no model-level validator, so no
migration was needed. nginx must allow it: `client_max_body_size 12M;` (see
`docs/deploy-checklist.md`). Pages show resized WebP copies, so a large upload
does not slow the website down.

Original policy (2026-07-20): all active website image uploads are optional and have no Django-level file-size limit.

Implemented changes:

- `initiator2023/settings.py`: `DATA_UPLOAD_MAX_MEMORY_SIZE = None`
- `initiator2023/settings.py`: `FILE_UPLOAD_MAX_MEMORY_SIZE = 0`
- `initiator2023/local_settings.py`: same local upload handling
- `web2.models.ProductUpload.file`: removed file-size validator
- `web2.models.Blog.image`: now optional with `blank=True` and `default=''`
- `web2.models.Blog.alt`: now optional with `blank=True` and `default=''`
- Migration added: `web2/migrations/0043_alter_blog_alt_alter_blog_image_and_more.py`

Historical validator functions are kept as no-op functions for migration compatibility. They do not reject uploaded files.

Important deployment note: Django no longer enforces a size limit, but production hosting can still limit uploads through Nginx, Apache, IIS, Cloudflare, load balancers, or hosting control panels. Increase those external limits separately if required.

## No Image Fallback

When a CMS record has no image, the frontend now shows a consistent default icon placeholder:

- Template partial: `templates/web2/partials/no_image.html`
- CSS class: `.no-image-placeholder`
- Broken uploaded image URLs are replaced by JavaScript in `static/web2/assets/js/main.js`

Fallback variants:

- `no-image-hero`: large hero/banner image areas
- `no-image-card`: product, service, module, blog, and portfolio cards
- `no-image-detail`: product/service/blog detail media
- `no-image-recent`: recent blog sidebar thumbnails

Updated pages include:

- Home page landing banner, about image, and landing service cards
- Product catalog and product detail
- Service catalog, module page, and service detail
- Legacy product/service templates
- Blog listing, blog detail, and recent posts sidebar
- Portfolio hero, featured case study, and selected work cards

## Recommended Image Dimensions

These are design recommendations only. They are not upload limits.

| Module / Model | Field | Display Area | Recommended Dimension |
| --- | --- | --- | --- |
| `Lan_PageBanModel` | `img` | Home hero banner | 1400 x 1000 px |
| `Lan_AboutusModel` | `img` | Home about section | 1200 x 900 px |
| `Product` | `img` | Product card | 1200 x 800 px |
| `Product` | `img` | Product detail page | 1400 x 1000 px |
| `Tally_Prime_Model` | `img` | Legacy product card | 1200 x 800 px |
| `All_AccoutingModel` | `img` | Legacy accounting product card | 1200 x 800 px |
| `All_ERPModel` | `img` | Legacy ERP product card | 1200 x 800 px |
| `Lan_ProductModel` | `img` | Landing product content | 1200 x 800 px |
| `Service` | `img` | Service card | 1200 x 800 px |
| `Service` | `img` | Service/module detail page | 1400 x 1000 px |
| `WebDevModel` | `img` | Legacy service card | 1200 x 800 px |
| `Web_DesignModel` | `img` | Legacy web design card | 1200 x 800 px |
| `Web_Portal_Dev` | `img` | Legacy portal card | 1200 x 800 px |
| `MobileAppModel` | `img` | Legacy mobile app card | 1200 x 800 px |
| `Tally_Customization` | `img` | Legacy Tally customization card | 1200 x 800 px |
| `Tally_VerticalModel` | `img` | Legacy module card | 1200 x 800 px |
| `Tally_CloudModel` | `img` | Legacy Tally cloud card | 1200 x 800 px |
| `Digital_Mkt_Model` | `img` | Legacy digital marketing card | 1200 x 800 px |
| `Graphics_Model` | `img` | Legacy graphics card | 1200 x 800 px |
| `CloudModel` | `img` | Legacy cloud service card | 1200 x 800 px |
| `Lan_ServicesModel` | `img` | Landing service content | 1200 x 800 px |
| `Blog` | `image` | Blog featured/listing/detail image | 1600 x 900 px |
| `Blog` | `image` | Recent post sidebar thumbnail | 600 x 400 px |
| `PortfolioModel` | `img` | Portfolio featured card | 1400 x 1000 px |
| `PortfolioModel` | `img` | Portfolio grid card | 1200 x 900 px |
| `SiteSEO` | `default_og_image` | Open Graph/Twitter fallback image | 1200 x 630 px |
| `ProductUpload` | `file` | Product attachment/gallery file | Original size accepted |

## Verification Completed

- Django system check passed.
- Django `web2` test suite passed.
- JavaScript syntax check passed.
- Public route HTTP crawl passed.
- Sitemap route crawl passed for 37 URLs.
- Browser GUI checks passed on desktop and mobile.
- Hamburger menu opens as a full mobile drawer.
- Enquiry modal opens and contains all required fields.
- No broken content images found in browser crawl.
- No horizontal overflow found in desktop/mobile browser crawl.
- SEO/schema JSON-LD parsed successfully across all sitemap URLs.

## SEO Schema Checked

Every sitemap URL includes:

- Canonical URL
- Robots meta tag
- One standard meta description
- Absolute Open Graph image
- Valid JSON-LD

Schema types verified:

- `Organization`
- `LocalBusiness`
- `WebSite`
- `WebPage`
- `CollectionPage`
- `ContactPage`
- `AboutPage`
- `BreadcrumbList`
- `Product`
- `Service`
- `Blog`
- `Article`
- `BlogPosting`
