# Deploy checklist (live server)

Run on the server from the project folder with the server virtualenv active.
Local development on Windows uses SQLite automatically (`manage.py` picks
`initiator2023.local_settings` on Windows); the Linux server keeps
`initiator2023.settings`.

## 1. Before uploading

```bash
pg_dump -U initiator2023 initiator2023 > ~/backup_$(date +%F_%H%M).sql
```

## 2. Upload the code

- Make sure `static/admin/` does **not** exist on the server (an old copy of
  Django admin files there breaks the admin layout).

## 3. Migrate and check (before restarting gunicorn)

```bash
python manage.py check --deploy
python manage.py migrate                      # 0044-0047: groups, SEO fields
python manage.py apply_seo_content --dry-run  # review the list
python manage.py apply_seo_content            # site SEO + 10 service pages
python manage.py check_site_data              # renders every page; exit 1 = fix first
python manage.py optimize_images              # small WebP copies of uploaded images
```

`optimize_images` makes the resized WebP copies that pages now show instead of
the multi-MB uploads (hero 2.3 MB -> 180 KB, product cards 7 MB -> 70 KB). It is
optional: a missing copy is made by the first visitor who needs it. Copies are
stored in `MEDIA_ROOT/_optimized/`; originals are never changed.

`check_site_data` is read-only. It reports pages that would crash, image files
missing on the server, invalid group slugs and counters that are not numbers.

## 4. Static files and restart

```bash
rm -rf <STATIC_ROOT>/admin        # old admin files may look newer than Django's
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn   # use your service name
sudo nginx -t && sudo systemctl reload nginx
```

## 5. After restart

```bash
curl -sIL http://initiatorsolutions.com | grep -iE "^HTTP|^location"   # one 301 to https://www., then 200
curl -s https://www.initiatorsolutions.com/robots.txt
curl -sI https://www.initiatorsolutions.com/sitemap.xml
curl -sI https://www.initiatorsolutions.com/this-page-does-not-exist/   # 404
```

Then in admin: upload images for new pages without one, enable IndexNow in
Site SEO Settings, and fill founder name / founding year.

## Rollback

```bash
python manage.py migrate web2 0043   # reverses 0044-0047 and restores old group values
```
Then restore the previous code (or the `pg_dump` backup).

## nginx: compression and browser caching (recommended)

Inside the existing `server { listen 443 ... }` block for www:

```nginx
gzip on;
gzip_types text/css application/javascript text/plain application/json image/svg+xml;

location /static/ {
    # keep your existing alias/root line
    expires 30d;
    add_header Cache-Control "public";
}

# Optional: nginx serves the WebP copies directly; Django makes missing ones.
location ~ ^/web2/img/(\d+)/(.+)$ {
    root <MEDIA_ROOT>/_optimized;        # e.g. /path/to/project/static/dynamic_images/_optimized
    default_type image/webp;
    try_files /$1/$2.webp @django;
    expires 30d;
    add_header Cache-Control "public";
}
```

`@django` is the named location that proxies to gunicorn; if your config only
has `location / { proxy_pass ... }`, add `location @django { proxy_pass ...; }`
with the same proxy lines, or skip the optional block (Django serves the copies
with a 30-day cache header either way).

## nginx: one main address

`https://initiatorsolutions.com` must redirect to `https://www.initiatorsolutions.com`:

```nginx
server {
    listen 80;
    server_name initiatorsolutions.com www.initiatorsolutions.com;
    return 301 https://www.initiatorsolutions.com$request_uri;
}
server {
    listen 443 ssl;
    server_name initiatorsolutions.com;
    # keep the ssl_certificate lines certbot added
    return 301 https://www.initiatorsolutions.com$request_uri;
}
```
