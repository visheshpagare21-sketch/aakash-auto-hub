from django.http import HttpResponse
from urllib.parse import quote

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from catalog.models import Category, Product
from core.models import BusinessInfo, EnquiryLog
from django.db.models import Q
from django.shortcuts import render
from catalog.models import Product
# from django.db.models import Q
# from catalog.models import Product


def home(request):
    categories = (
        Category.objects.filter(is_active=True)
        .annotate(active_product_count=Count('products', filter=Q(products__is_active=True)))
        .order_by('display_order', 'name')
    )
    featured_products = (
        Product.objects.filter(is_active=True, is_featured=True)
        .select_related('category')
        .prefetch_related('images')[:8]
    )
    return render(
        request,
        'core/home.html',
        {
            'categories': categories,
            'featured_products': featured_products,
        },
    )


def search(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.none()
    if query:
        products = (
            Product.objects.filter(is_active=True)
            .filter(
                Q(name__icontains=query)
                | Q(part_number__icontains=query)
                | Q(description__icontains=query)
                | Q(category__name__icontains=query)
            )
            .select_related('category')
            .prefetch_related('images')
        )
    return render(request, 'core/search_results.html', {'query': query, 'products': products})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    subcategories = category.subcategories.filter(is_active=True).order_by('display_order', 'name')
    selected_subcategory = request.GET.get('sub', '').strip()
    products = (
        category.products.filter(is_active=True)
        .select_related('category', 'sub_category')
        .prefetch_related('images')
    )
    if selected_subcategory:
        products = products.filter(sub_category__slug=selected_subcategory)

    page_obj = Paginator(products, 12).get_page(request.GET.get('page'))
    business_info = BusinessInfo.get_solo()
    whatsapp_number = ''.join(char for char in business_info.whatsapp_number if char.isdigit())
    empty_whatsapp_url = ''
    if whatsapp_number:
        message = f'Hi, I am looking for {category.name} AC parts. Please share availability.'
        empty_whatsapp_url = f'https://wa.me/{whatsapp_number}?text={quote(message)}'

    return render(
        request,
        'core/category_detail.html',
        {
            'category': category,
            'subcategories': subcategories,
            'selected_subcategory': selected_subcategory,
            'page_obj': page_obj,
            'empty_whatsapp_url': empty_whatsapp_url,
        },
    )


def legacy_category_detail(request, slug):
    return redirect('category-detail', slug=slug, permanent=True)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.filter(is_active=True).select_related('category').prefetch_related('images'),
        slug=slug,
    )
    business_info = BusinessInfo.get_solo()
    whatsapp_number = ''.join(
        char for char in (business_info.whatsapp_number or business_info.phone_number) if char.isdigit()
    )
    try:
        message = business_info.whatsapp_message_template.format(
            product_name=product.name,
            part_number=product.part_number or 'N/A',
        )
    except (KeyError, ValueError):
        message = f'Hi, I am interested in {product.name} (Part No: {product.part_number or "N/A"}).'

    whatsapp_url = ''
    if whatsapp_number:
        whatsapp_url = f'https://wa.me/{whatsapp_number}?text={quote(message)}'

    compatible_models = [
        model.strip()
        for model in product.compatible_models.replace('\n', ',').split(',')
        if model.strip()
    ]
    related_products = (
        product.alternative_parts.filter(is_active=True)
        .select_related('category')
        .prefetch_related('images')[:4]
    )
    return render(
        request,
        'core/product_detail.html',
        {
            'product': product,
            'whatsapp_url': whatsapp_url,
            'call_url': f'tel:{"".join(char for char in business_info.phone_number if char.isdigit() or char == "+")}',
            'compatible_models': compatible_models,
            'related_products': related_products,
        },
    )


@csrf_exempt
@require_POST
def log_whatsapp_enquiry(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    EnquiryLog.objects.create(product=product, source=EnquiryLog.Source.WHATSAPP)
    return JsonResponse({'ok': True})


def categories(request):
    return render(
        request,
        'core/dummy_page.html',
        {
            'page_title': 'Categories',
            'page_kicker': 'Catalog',
            'page_summary': 'Browse our main AC parts categories and quickly find the right section for buses and cars.',
            'page_key': 'categories',
        },
    )


def about(request):
    return render(
        request,
        'core/dummy_page.html',
        {
            'page_title': 'About',
            'page_kicker': 'Aakash Auto Hub',
            'page_summary': 'A focused auto AC parts partner built around genuine parts, sharp pricing, and practical guidance.',
            'page_key': 'about',
        },
    )


def contact(request):
    return render(
        request,
        'core/dummy_page.html',
        {
            'page_title': 'Contact',
            'page_kicker': 'Talk to an Expert',
            'page_summary': 'Reach out for availability, compatible part suggestions, pricing, and fast dispatch support.',
            'page_key': 'contact',
        },
    )


def search(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(part_number__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        ).distinct()

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'core/search_results.html', context)

def robots_txt(request):
    return HttpResponse(
        "User-agent: *\n"
        "Allow: /\n\n"
        "Sitemap: https://aakashautohub.com/sitemap.xml",
        content_type="text/plain",
    )