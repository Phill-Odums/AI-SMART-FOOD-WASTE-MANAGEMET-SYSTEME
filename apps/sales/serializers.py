"""Serializers for Sales Records application."""

from decimal import Decimal

from rest_framework import serializers

from .models import SalesRecord, ShiftChoices


class SalesRecordSerializer(serializers.ModelSerializer):
    """Full detail and create/update serializer for individual sales records."""

    shift_display = serializers.CharField(
        source='get_shift_display', read_only=True
    )

    class Meta:
        model = SalesRecord
        fields = [
            'id',
            'branch',
            'menu_item',
            'sale_date',
            'shift',
            'shift_display',
            'quantity_sold',
            'total_revenue_naira',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SalesRecordListSerializer(serializers.ModelSerializer):
    """Optimized list serializer including related branch and menu item names."""

    branch_name = serializers.CharField(source='branch.name', read_only=True)
    menu_item_name = serializers.CharField(
        source='menu_item.name', read_only=True
    )
    shift_display = serializers.CharField(
        source='get_shift_display', read_only=True
    )

    class Meta:
        model = SalesRecord
        fields = [
            'id',
            'branch',
            'branch_name',
            'menu_item',
            'menu_item_name',
            'sale_date',
            'shift',
            'shift_display',
            'quantity_sold',
            'total_revenue_naira',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'branch_name',
            'menu_item_name',
            'created_at',
            'updated_at',
        ]


class SingleSalesRecordItemSerializer(serializers.Serializer):
    """Payload schema for an individual sales record in bulk ingestion."""

    branch = serializers.UUIDField(help_text='Branch outlet UUID')
    menu_item = serializers.UUIDField(help_text='Menu item UUID')
    sale_date = serializers.DateField(help_text='Date of sale (YYYY-MM-DD)')
    shift = serializers.ChoiceField(
        choices=ShiftChoices.choices,
        help_text='Shift category (morning_lunch, evening_dinner, full_day)',
    )
    quantity_sold = serializers.IntegerField(
        min_value=0, help_text='Units or portions sold'
    )
    total_revenue_naira = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0'),
        help_text='Total shift revenue in ₦',
    )


class BulkSalesUploadSerializer(serializers.Serializer):
    """Non-model serializer for bulk POS transaction upload."""

    records = serializers.ListField(
        child=SingleSalesRecordItemSerializer(),
        allow_empty=False,
        help_text='List of sales record objects for bulk database insertion',
    )
