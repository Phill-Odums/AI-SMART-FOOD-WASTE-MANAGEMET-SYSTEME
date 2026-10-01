"""Django Admin configuration for the AI Demand Forecasting application."""

import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import DailyForecastItem, ForecastRun, KitchenPrepTarget


def export_as_csv_action(description="Export selected to CSV"):
    def export_as_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{opts.verbose_name_plural}.csv"'
        writer = csv.writer(response)
        field_names = [field.name for field in opts.fields]
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response

    export_as_csv.short_description = description
    return export_as_csv


class DailyForecastItemInline(admin.TabularInline):
    model = DailyForecastItem
    extra = 0
    readonly_fields = [
        'ensemble_prediction',
        'disagreement_score',
        'confidence_level',
        'recommended_prep_strategy',
        'batch_1_portions',
        'batch_2_portions',
        'batch_3_portions',
    ]


class KitchenPrepTargetInline(admin.TabularInline):
    model = KitchenPrepTarget
    extra = 0
    readonly_fields = ['variance_qty']


@admin.register(ForecastRun)
class ForecastRunAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'branch',
        'forecast_target_date',
        'status',
        'executed_at',
    ]
    list_filter = ['status', 'forecast_target_date', 'branch__city']
    search_fields = ['branch__name', 'notes']
    date_hierarchy = 'forecast_target_date'
    inlines = [DailyForecastItemInline, KitchenPrepTargetInline]
    actions = [export_as_csv_action("Export selected forecast runs to CSV")]


@admin.register(DailyForecastItem)
class DailyForecastItemAdmin(admin.ModelAdmin):
    list_display = [
        'forecast_run',
        'menu_item',
        'chronos_prediction',
        'timesfm_prediction',
        'ensemble_prediction',
        'disagreement_score',
        'confidence_level',
        'recommended_prep_strategy',
        'batch_1_portions',
        'batch_2_portions',
    ]
    list_filter = ['confidence_level', 'recommended_prep_strategy', 'forecast_run__branch']
    search_fields = ['menu_item__name', 'forecast_run__branch__name']
    actions = [export_as_csv_action("Export selected forecast items to CSV")]


@admin.register(KitchenPrepTarget)
class KitchenPrepTargetAdmin(admin.ModelAdmin):
    list_display = [
        'forecast_run',
        'ingredient',
        'total_raw_qty_to_prep',
        'actual_used_qty',
        'variance_qty',
    ]
    list_filter = ['forecast_run__branch', 'ingredient']
    search_fields = ['ingredient__name', 'forecast_run__branch__name']
    actions = [export_as_csv_action("Export selected prep targets to CSV")]
