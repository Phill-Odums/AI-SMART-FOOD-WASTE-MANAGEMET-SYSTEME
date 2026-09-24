"""Django Admin configuration for the Analytics application."""

from django.contrib import admin
from .models import MenuEngineeringSnapshot, PilotKPISnapshot


@admin.register(MenuEngineeringSnapshot)
class MenuEngineeringSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        'menu_item',
        'branch',
        'matrix_category',
        'units_sold',
        'waste_weight_kg',
        'revenue_naira',
        'profit_margin_naira',
        'period_start',
        'period_end',
    ]
    list_filter = ['matrix_category', 'branch__city', 'period_end']
    search_fields = ['menu_item__name', 'branch__name', 'recommendation']
    date_hierarchy = 'period_end'


@admin.register(PilotKPISnapshot)
class PilotKPISnapshotAdmin(admin.ModelAdmin):
    list_display = [
        'branch',
        'period_label',
        'snapshot_date',
        'total_waste_kg',
        'total_waste_cost_naira',
        'total_sales_revenue_naira',
        'waste_to_revenue_ratio',
        'forecast_accuracy_mape',
    ]
    list_filter = ['period_label', 'branch__is_pilot_intervention', 'branch__city']
    search_fields = ['branch__name']
    date_hierarchy = 'snapshot_date'
