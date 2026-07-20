from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category', 'display_order', 'is_active', 'icon_preview')
    list_editable = ('display_order', 'is_active')
    list_filter = ('is_active', 'parent_category')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')
    readonly_fields = ('icon_preview',)

    fieldsets = (
        ('Category Details', {
            'fields': ('name', 'slug', 'parent_category', 'icon_image', 'icon_preview'),
        }),
        ('Display Settings', {
            'fields': ('display_order', 'is_active'),
        }),
    )

    @admin.display(description='Icon')
    def icon_preview(self, obj):
        if obj and obj.icon_image:
            return format_html(
                '<img src="{}" style="height:42px;width:42px;object-fit:cover;border-radius:8px;">',
                obj.icon_image.url,
            )
        return 'No icon'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_primary', 'image_preview')
    readonly_fields = ('image_preview',)

    @admin.display(description='Preview')
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="height:56px;width:72px;object-fit:cover;border-radius:8px;">',
                obj.image.url,
            )
        return 'Upload image'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'is_featured')
    list_editable = ('is_active', 'is_featured')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'part_number')
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('category', 'sub_category', 'alternative_parts')
    filter_horizontal = ('alternative_parts',)
    readonly_fields = ('created_at',)
    inlines = (ProductImageInline,)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Product Details', {
            'fields': ('name', 'slug', 'part_number', 'description'),
        }),
        ('Classification', {
            'fields': ('category', 'sub_category', 'compatible_models', 'alternative_parts'),
        }),
        ('Publishing', {
            'fields': ('is_active', 'is_featured', 'created_at'),
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary', 'image_preview')
    list_filter = ('is_primary',)
    search_fields = ('product__name', 'product__part_number')
    autocomplete_fields = ('product',)
    readonly_fields = ('image_preview',)

    @admin.display(description='Preview')
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="height:56px;width:72px;object-fit:cover;border-radius:8px;">',
                obj.image.url,
            )
        return 'No image'
