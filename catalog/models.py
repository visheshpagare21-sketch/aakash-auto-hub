from django.db import models
from django.utils.text import slugify


def generate_unique_slug(instance, value):
    model_class = instance.__class__
    slug_field = instance._meta.get_field('slug')
    max_length = slug_field.max_length
    base_slug = slugify(value)[:max_length] or 'item'
    slug = base_slug
    counter = 2

    queryset = model_class.objects.filter(slug=slug)
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    while queryset.exists():
        suffix = f'-{counter}'
        slug = f'{base_slug[: max_length - len(suffix)]}{suffix}'
        queryset = model_class.objects.filter(slug=slug)
        if instance.pk:
            queryset = queryset.exclude(pk=instance.pk)
        counter += 1

    return slug


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    icon_image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='subcategories',
    )
    display_order = models.PositiveIntegerField(default=0)
    show_on_homepage = models.BooleanField(default=False)
    homepage_order = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'display_order']),
            models.Index(fields=['is_active', 'show_on_homepage', 'homepage_order']),
        ]

    def __str__(self):
        if self.parent_category:
            return f'{self.parent_category} > {self.name}'
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    part_number = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
    )
    sub_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='sub_products',
    )
    compatible_models = models.TextField(blank=True)
    alternative_parts = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='alternative_to',
    )
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', 'name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['part_number']),
            models.Index(fields=['is_active', 'is_featured']),
        ]

    def __str__(self):
        if self.part_number:
            return f'{self.name} ({self.part_number})'
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_primary', 'id']
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'

    def __str__(self):
        primary_label = 'Primary' if self.is_primary else 'Gallery'
        return f'{self.product} - {primary_label} image'
