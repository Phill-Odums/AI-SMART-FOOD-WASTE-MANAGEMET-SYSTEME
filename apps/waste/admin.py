"""Django Admin configuration for Waste Tracking application."""

from django.contrib import admin

from .models import WasteLog


@admin.register(WasteLog)
class WasteLogAdmin(admin.ModelAdmin):
    """Admin interface for reviewing and auditing food waste events."""

    list_display = [
        'id',
        'branch',
        'operational_stage',
        'menu_item',
        'ingredient',
        'weight_kg',
        'financial_loss_naira',
        'root_cause_determinant',
        'timestamp',
    ]
    list_filter = [
        'operational_stage',
        'root_cause_determinant',
        'branch',
        'timestamp',
    ]
    search_fields = [
        'notes',
        'branch__name',
        'menu_item__name',
        'ingredient__name',
    ]
    date_hierarchy = 'timestamp'
    readonly_fields = ['id', 'timestamp', 'financial_loss_naira']
    ordering = ['-timestamp']
