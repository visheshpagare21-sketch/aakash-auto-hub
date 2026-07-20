from django import template
from django.db.models import Count
from django.utils import timezone

from catalog.models import Category, Product
from core.models import EnquiryLog

register = template.Library()


@register.simple_tag
def admin_dashboard_stats():
    now = timezone.localtime()
    top_products = (
        Product.objects.annotate(enquiry_count=Count('enquiry_logs'))
        .filter(enquiry_count__gt=0)
        .order_by('-enquiry_count', 'name')[:5]
    )

    return {
        'total_products': Product.objects.count(),
        'active_products': Product.objects.filter(is_active=True).count(),
        'total_categories': Category.objects.count(),
        'active_categories': Category.objects.filter(is_active=True).count(),
        'enquiries_this_month': EnquiryLog.objects.filter(
            clicked_at__year=now.year,
            clicked_at__month=now.month,
        ).count(),
        'top_products': top_products,
    }
