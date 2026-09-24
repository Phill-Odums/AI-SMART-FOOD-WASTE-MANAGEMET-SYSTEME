"""Django Admin configuration for Local Calendar Context application."""

from django.contrib import admin

from .models import LocalCalendarContext


@admin.register(LocalCalendarContext)
class LocalCalendarContextAdmin(admin.ModelAdmin):
    """Admin interface for managing regional calendar variables and events."""

    list_display = [
        'city',
        'date',
        'traditional_market_day',
        'is_major_market_day',
        'is_payday_window',
        'is_sunday_church_surge',
        'is_public_holiday',
        'weather_flag',
    ]
    list_filter = [
        'city',
        'traditional_market_day',
        'is_major_market_day',
        'is_payday_window',
        'is_sunday_church_surge',
        'is_public_holiday',
        'weather_flag',
        'date',
    ]
    search_fields = [
        'city',
        'public_holiday_name',
        'custom_event_note',
    ]
    date_hierarchy = 'date'
    ordering = ['-date', 'city']
    readonly_fields = ['id', 'created_at', 'updated_at']
