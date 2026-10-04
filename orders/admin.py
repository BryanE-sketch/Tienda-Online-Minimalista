from django.contrib import admin
from django.db.models import DecimalField, F, Sum

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'status', 'total_display', 'created_at']
    list_filter = ['status', 'created_at']
    list_select_related = ['user']
    search_fields = ['id', 'full_name', 'user__username', 'user__email']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['user']
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _total=Sum(
                F('items__unit_price') * F('items__quantity'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )

    @admin.display(description='total', ordering='_total')
    def total_display(self, obj):
        return f'{obj._total or 0:.2f} €'