from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'unit_price', 'quantity']
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'status', 'total_display', 'created_at']
    list_filter = ['status', 'created_at']
    list_select_related = ['user']
    search_fields = ['id', 'full_name', 'user__username', 'user__email']
    date_hierarchy = 'created_at'
    readonly_fields = ['user', 'status']
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        return super().get_queryset(request).with_total()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description='total', ordering='total_amount')
    def total_display(self, obj):
        return f'{obj.total_amount or 0:.2f} €'