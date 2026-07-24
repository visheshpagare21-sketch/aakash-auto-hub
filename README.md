# Aakash Auto Hub - Bus & Car AC Parts Catalog

Django product catalog for auto AC parts. Customers browse products and enquire directly through WhatsApp or phone; no prices or online payments are shown.

## Local Setup

1. Create a virtual environment: `python -m venv .venv`
2. Activate it: `.venv\Scripts\activate` on Windows
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env`, then use local values with `DEBUG=True`
5. Run migrations: `python manage.py migrate`
6. Create an owner account: `python manage.py createsuperuser`
7. Start the app: `python manage.py runserver`

Visit `/admin/` to manage categories, products, business details, and enquiry logs.

## Hostinger VPS Deployment

The project is configured for a Linux VPS with Nginx, Gunicorn, and systemd.

1. Install packages: `sudo apt update && sudo apt install python3-venv python3-pip nginx`
2. Upload/clone this project to `/var/www/aakash-auto-hub`, create a virtual environment, and install `requirements.txt`.
3. Copy `.env.example` to `.env`. Set a new random `SECRET_KEY`, `DEBUG=False`, the real `ALLOWED_HOSTS`, and the HTTPS `CSRF_TRUSTED_ORIGINS` values.
4. Run `python manage.py migrate` and `python manage.py collectstatic --noinput`.
5. Copy `deployment/aakash-auto-hub.service` to `/etc/systemd/system/`, adjust its paths/user if needed, then run `sudo systemctl daemon-reload && sudo systemctl enable --now aakash-auto-hub`.
6. Copy `deployment/nginx-aakash-auto-hub.conf` to `/etc/nginx/sites-available/`, replace `server_name`, enable the site, run `sudo nginx -t`, then reload Nginx.
7. Add SSL, for example: `sudo certbot --nginx -d your-domain.com -d www.your-domain.com`.

By default, uploaded media is stored in `/media/` and served by Nginx. Cloudinary is optional: set `USE_CLOUDINARY=True` plus its three Cloudinary credentials in the VPS `.env`.
