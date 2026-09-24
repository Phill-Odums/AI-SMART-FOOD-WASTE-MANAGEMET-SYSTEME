"""Django Admin configuration for Sales Records application."""

from django.contrib import admin

from .models import SalesRecord


@admin.register(SalesRecord)
class SalesRecordAdmin(admin.ModelAdmin):
    """Admin interface for monitoring POS sales ingestion and historical sales."""

    list_display = [
        'id',
        'branch',
        'menu_item',
        'sale_date',
        'shift',
        'quantity_sold',
        'total_revenue_naira',
        'created_at',
    ]
    list_filter = [
        'shift',
        'branch',
        'sale_date',
    ]
    search_fields = [
        'menu_item__name',
        'branch__name',
    ]
    date_hierarchy = 'sale_date'
    ordering = ['-sale_date']
    readonly_fields = ['id', 'created_at', 'updated_at']
