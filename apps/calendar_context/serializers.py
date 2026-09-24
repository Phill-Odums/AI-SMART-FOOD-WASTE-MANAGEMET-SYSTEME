"""Serializers for Local Calendar Context application."""

from rest_framework import serializers

from .models import LocalCalendarContext


class LocalCalendarContextSerializer(serializers.ModelSerializer):
    """Standard serializer for local calendar context entries."""

    market_day_display = serializers.CharField(
        source='get_traditional_market_day_display', read_only=True
    )
    weather_display = serializers.CharField(
        source='get_weather_flag_display', read_only=True
    )

    class Meta:
        model = LocalCalendarContext
        fields = [
            'id',
            'date',
            'city',
            'traditional_market_day',
            'market_day_display',
            'is_major_market_day',
            'is_payday_window',
            'is_sunday_church_surge',
            'is_public_holiday',
            'public_holiday_name',
            'weather_flag',
            'weather_display',
            'custom_event_note',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TodayContextSerializer(LocalCalendarContextSerializer):
    """Context serializer for current day with computed day_of_week name."""

    day_of_week = serializers.SerializerMethodField(
        help_text='Name of the day of the week, e.g. Monday, Sunday'
    )

    class Meta(LocalCalendarContextSerializer.Meta):
        fields = LocalCalendarContextSerializer.Meta.fields + ['day_of_week']

    def get_day_of_week(self, obj) -> str:
        """Return the formatted weekday name."""
        return obj.date.strftime('%A') if obj.date else ''
