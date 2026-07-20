from django.contrib import admin

from .models import BusinessInfo, EnquiryLog


@admin.register(BusinessInfo)
class BusinessInfoAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'tagline', 'phone_number', 'whatsapp_number', 'email')
    fieldsets = (
        ('Branding', {
            'fields': ('business_name', 'tagline', 'logo', 'about_text'),
        }),
        ('Contact Details', {
            'fields': ('phone_number', 'whatsapp_number', 'email', 'address', 'map_embed_link'),
        }),
        ('WhatsApp Enquiry Message', {
            'fields': ('whatsapp_message_template',),
            'description': (
                'Use {product_name} and {part_number} placeholders. '
                'They will be replaced automatically on product enquiry links.'
            ),
        }),
        ('Social Links', {
            'fields': ('instagram_url', 'facebook_url'),
        }),
    )

    def has_add_permission(self, request):
        if BusinessInfo.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(EnquiryLog)
class EnquiryLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'source', 'clicked_at')
    list_filter = ('source', 'clicked_at')
    search_fields = ('product__name', 'product__part_number')
    readonly_fields = ('product', 'source', 'clicked_at')
    date_hierarchy = 'clicked_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
