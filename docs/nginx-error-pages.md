# Nginx Error Pages

Use Django for application errors that reach the app:

- 404: handled by `web2.views.custom_404`
- 500: handled by `web2.views.custom_500`

Use nginx for gateway errors, because Django cannot render a response when nginx cannot reach the upstream application.

Example nginx block:

```nginx
error_page 502 503 504 /static/error_pages/502.html;

location = /static/error_pages/502.html {
    root /path/to/initiator_solutions_live-main-3;
    internal;
}
```

If production serves collected static files from a different directory, point `root` to the directory that contains the `static` folder. For example, if `/var/www/initiator/static/error_pages/502.html` exists, use:

```nginx
location = /static/error_pages/502.html {
    root /var/www/initiator;
    internal;
}
```

After changing nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

For a live 502, check:

- `sudo journalctl -u nginx -n 100`
- `sudo tail -n 100 /var/log/nginx/error.log`
- `sudo systemctl status gunicorn`
- the Django/Gunicorn application log around the same timestamp
