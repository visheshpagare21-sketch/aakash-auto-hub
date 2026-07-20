from django.core.exceptions import ValidationError
from django.db import models


class BusinessInfo(models.Model):
    business_name = models.CharField(max_length=160, default='Aakash Auto Hub')
    tagline = models.CharField(
        max_length=220,
        default='Bus & Car AC Parts Specialist',
        blank=True,
    )
    logo = models.ImageField(upload_to='business/', blank=True, null=True)
    about_text = models.TextField(blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    whatsapp_number = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True, default='')
    whatsapp_message_template = models.TextField(
        default=(
            "Hi, I'm interested in {product_name} (Part No: {part_number}). "
            'Please share more details.'
        )
    )
    address = models.TextField(blank=True)
    map_embed_link = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)

    class Meta:
        verbose_name = 'Business Info'
        verbose_name_plural = 'Business Info'

    def __str__(self):
        return self.business_name

    def clean(self):
        if not self.pk and BusinessInfo.objects.exists():
            raise ValidationError('Only one BusinessInfo record is allowed.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        business_info, _created = cls.objects.get_or_create(
            defaults={
                'business_name': 'Aakash Auto Hub',
                'tagline': 'Bus & Car AC Parts Specialist',
            }
        )
        return business_info


class EnquiryLog(models.Model):
    class Source(models.TextChoices):
        WHATSAPP = 'whatsapp', 'WhatsApp'
        CALL = 'call', 'Call'

    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        related_name='enquiry_logs',
    )
    clicked_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=20, choices=Source.choices)

    class Meta:
        ordering = ['-clicked_at']
        verbose_name = 'Enquiry Log'
        verbose_name_plural = 'Enquiry Logs'
        indexes = [
            models.Index(fields=['clicked_at']),
            models.Index(fields=['source']),
        ]

    def __str__(self):
        return f'{self.product} - {self.get_source_display()} enquiry'
