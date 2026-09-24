"""Django Admin configuration for Inventory app."""

from django.contrib import admin
from .models import InventoryBatch, PowerOutageLog


@admin.register(InventoryBatch)
class InventoryBatchAdmin(admin.ModelAdmin):
    """Admin configuration for raw ingredient inventory batches."""
    list_display = [
        'ingredient',
        'branch',
        'quantity_remaining',
        'quantity_received',
        'storage_type',
        'expiry_date',
        'is_depleted',
        'unit_cost_at_purchase',
        'received_date',
        'created_at',
    ]
    list_filter = ['storage_type', 'is_depleted', 'branch', 'ingredient']
    search_fields = ['ingredient__name', 'branch__name', 'notes']
    ordering = ['expiry_date']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(PowerOutageLog)
class PowerOutageLogAdmin(admin.ModelAdmin):
    """Admin configuration for power outage logs."""
    list_display = [
        'branch',
        'outage_start',
        'outage_end',
        'generator_available',
        'duration_display',
        'created_at',
    ]
    list_filter = ['branch', 'generator_available']
    search_fields = ['branch__name', 'notes']
    ordering = ['-outage_start']
    readonly_fields = ['id', 'created_at']

    @admin.display(description='Duration (Hours)')
    def duration_display(self, obj):
        hours = obj.duration_hours
        return f"{hours:.2f} hrs" if hours is not None else "Ongoing"
