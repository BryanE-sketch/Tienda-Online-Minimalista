from django.contrib import admin
from django.db.models import Count

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
    list_display = ['name', 'category', 'price', 'stock', 'is_active']
    list_editable = ['price', 'stock', 'is_active']
    list_filter = ['is_active', 'category']
    list_select_related = ['category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ['name']}