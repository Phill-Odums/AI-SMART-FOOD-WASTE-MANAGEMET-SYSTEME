"""Serializers for the Analytics application."""

from rest_framework import serializers
from .models import MenuEngineeringSnapshot, PilotKPISnapshot


class MenuEngineeringSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for menu engineering quadrant snapshots."""

    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    matrix_category_display = serializers.CharField(source='get_matrix_category_display', read_only=True)

    class Meta:
        model = MenuEngineeringSnapshot
        fields = [
            'id',
            'branch',
            'branch_name',
            'menu_item',
            'menu_item_name',
            'period_start',
            'period_end',
            'units_sold',
            'waste_weight_kg',
            'waste_cost_naira',
            'revenue_naira',
            'ingredient_cost_naira',
            'profit_margin_naira',
            'matrix_category',
            'matrix_category_display',
            'recommendation',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class PilotKPISnapshotSerializer(serializers.ModelSerializer):
    """Serializer for pilot quasi-experiment KPI evaluation snapshots."""

    branch_name = serializers.CharField(source='branch.name', read_only=True)
    is_intervention = serializers.BooleanField(source='branch.is_pilot_intervention', read_only=True)
    period_label_display = serializers.CharField(source='get_period_label_display', read_only=True)

    class Meta:
        model = PilotKPISnapshot
        fields = [
            'id',
            'branch',
            'branch_name',
            'is_intervention',
            'snapshot_date',
            'period_label',
            'period_label_display',
            'total_waste_kg',
            'total_waste_cost_naira',
            'total_sales_revenue_naira',
            'waste_to_revenue_ratio',
            'forecast_accuracy_mape',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'waste_to_revenue_ratio']


class GenerateMenuEngineeringSerializer(serializers.Serializer):
    """Input payload to trigger matrix analysis generation over an operational date range."""

    branch = serializers.UUIDField(help_text='UUID of the branch outlet to analyze')
    period_start = serializers.DateField(help_text='Start date of analysis period (YYYY-MM-DD)')
    period_end = serializers.DateField(help_text='End date of analysis period (YYYY-MM-DD)')

    def validate(self, attrs):
        if attrs['period_start'] > attrs['period_end']:
            raise serializers.ValidationError({
                'period_end': 'period_end must be greater than or equal to period_start.'
            })
        return attrs
