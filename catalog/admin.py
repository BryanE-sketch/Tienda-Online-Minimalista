from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ['name']}

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_product_count=Count('products'))

    @admin.display(description='productos', ordering='_product_count')
    def product_count(self, obj):
        return obj._product_count


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['thumbnail', 'name', 'category', 'price', 'stock', 'is_active']
    list_display_links = ['thumbnail', 'name']
    list_editable = ['price', 'stock', 'is_active']
    list_filter = ['is_active', 'category']
    list_select_related = ['category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ['name']}

    @admin.display(description='imagen')
    def thumbnail(self, obj):
        if not obj.image:
            return '—'
        return format_html(
            '<img src="{}" alt="" style="height: 40px; width: 40px; '
            'object-fit: cover; border-radius: 4px;">',
            obj.image.url,
        )