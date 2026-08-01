from urllib.parse import quote

from django.db.models import Count, Q
from django.templatetags.static import static

from catalog.models import Category
from core.models import BusinessInfo


def _phone_href(phone_number):
    cleaned = ''.join(char for char in phone_number if char.isdigit() or char == '+')
    if not cleaned:
        return ''
    return f'tel:{cleaned}'


def _whatsapp_url(phone_number, message):
    digits = ''.join(char for char in phone_number if char.isdigit())
    if not digits:
        return ''
    return f'https://wa.me/{digits}?text={quote(message)}'


def site_context(request):
    business_info = BusinessInfo.get_solo()

    try:
        whatsapp_message = business_info.whatsapp_message_template.format(
            product_name='your products',
            part_number='N/A',
        )
    except (KeyError, ValueError):
        whatsapp_message = business_info.whatsapp_message_template

    whatsapp_number = business_info.whatsapp_number or business_info.phone_number
    popular_categories = (
        Category.objects.filter(is_active=True, show_on_homepage=True)
        .annotate(active_product_count=Count('products', filter=Q(products__is_active=True)))
        .order_by('homepage_order', 'display_order', 'name')[:8]
    )

    return {
        'business_info': business_info,
        'site_logo_url': business_info.logo.url if business_info.logo else static('images/aakash-auto-hub-logo.png'),
        'site_contact': {
            'phone_href': _phone_href(business_info.phone_number),
            'whatsapp_url': _whatsapp_url(whatsapp_number, whatsapp_message),
        },
        'popular_categories': popular_categories,
        'site_trust_badges': [
            'Genuine Parts',
            'Best Price',
            'Expert Service',
            'Fast Delivery',
        ],
    }
