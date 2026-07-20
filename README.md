# Aakash Auto Hub — Bus & Car AC Parts Catalog

Django-based product catalog website. No online payments — customers browse
products and enquire directly via WhatsApp.

## Setup

1. Create virtual environment: `python -m venv .venv`
2. Activate it: `.venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Create admin user: `python manage.py createsuperuser`
6. Run server: `python manage.py runserver`

## Admin Panel

Visit `/admin/` and log in with your superuser credentials to manage:
- Categories
- Products
- Business Info (logo, contact details, social links)
- Enquiry Logs

## Environment Notes

- Media uploads go to `/media/`
- Static files (CSS/JS/images) are in `/static/`
- Before deploying, run `python manage.py collectstatic` and set `DEBUG = False`
  in settings.py, and add your live domain to `ALLOWED_HOSTS`.

## Deployment

Recommended: Render, Railway, or PythonAnywhere (Django-friendly hosts).