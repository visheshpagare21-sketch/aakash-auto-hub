from django.shortcuts import render
from django.http import HttpResponse
from urllib.parse import quote

from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.db.models.functions import Greatest
from django.contrib.postgres.search import TrigramSimilarity
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from catalog.models import Category, Product
from core.models import BusinessInfo, EnquiryLog


def _product_text_filter(query):
    return (
        Q(name__icontains=query)
        | Q(part_number__icontains=query)
        | Q(description__icontains=query)
        | Q(compatible_models__icontains=query)
        | Q(category__name__icontains=query)
    )


def _search_products(query, queryset=None):
    """Return exact and close product matches, with exact matches first."""
    products_queryset = queryset or Product.objects.filter(is_active=True)
    text_match = _product_text_filter(query)

    if connection.vendor != 'postgresql':
        return products_queryset.filter(text_match)

    return (
        products_queryset.annotate(
            exact_match=Case(
                When(text_match, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
            similarity_score=Greatest(
                TrigramSimilarity('name', query),
                TrigramSimilarity('part_number', query),
                TrigramSimilarity('description', query),
                TrigramSimilarity('compatible_models', query),
                TrigramSimilarity('category__name', query),
            ),
        )
        .filter(Q(exact_match=1) | Q(similarity_score__gte=0.14))
        .order_by('-exact_match', '-similarity_score', 'name')
    )


def _search_categories(query, queryset):
    if connection.vendor != 'postgresql':
        return queryset.filter(name__icontains=query)

    return (
        queryset.annotate(
            exact_match=Case(
                When(name__icontains=query, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
            similarity_score=TrigramSimilarity('name', query),
        )
        .filter(Q(exact_match=1) | Q(similarity_score__gte=0.14))
        .order_by('-exact_match', '-similarity_score', 'display_order', 'name')
    )


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
    business_info = BusinessInfo.get_solo()
    return render(
        request,
        'core/home.html',
        {
            'categories': categories,
            'featured_products': featured_products,
            'business_info': business_info,
        },
    )


def products(request):
    query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()
    categories = Category.objects.filter(is_active=True).order_by('display_order', 'name')
    products_queryset = (
        Product.objects.filter(is_active=True)
        .select_related('category')
        .prefetch_related('images')
    )

    if query:
        products_queryset = _search_products(query, products_queryset)
    if selected_category:
        products_queryset = products_queryset.filter(category__slug=selected_category)

    page_obj = Paginator(products_queryset, 12).get_page(request.GET.get('page'))
    return render(
        request,
        'core/products.html',
        {
            'categories': categories,
            'page_obj': page_obj,
            'query': query,
            'selected_category': selected_category,
        },
    )


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
    query = request.GET.get('q', '').strip()
    all_categories = (
        Category.objects.filter(is_active=True)
        .annotate(active_product_count=Count('products', filter=Q(products__is_active=True)))
        .order_by('display_order', 'name')
    )
    if query:
        all_categories = _search_categories(query, all_categories)

    return render(
        request,
        'core/categories.html',
        {
            'categories': all_categories,
            'query': query,
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
    results = Product.objects.none()

    if query:
        results = _search_products(
            query,
            Product.objects.filter(is_active=True).select_related('category').prefetch_related('images'),
        )

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
