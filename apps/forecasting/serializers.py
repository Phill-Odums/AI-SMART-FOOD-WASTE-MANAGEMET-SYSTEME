"""Serializers for the AI Demand Forecasting application."""

from decimal import Decimal
from rest_framework import serializers
from .models import ForecastRun, DailyForecastItem, KitchenPrepTarget


class DailyForecastItemSerializer(serializers.ModelSerializer):
    """Serializer for individual menu item predictions and batch recommendations."""

    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    confidence_level_display = serializers.CharField(source='get_confidence_level_display', read_only=True)
    recommended_prep_strategy_display = serializers.CharField(source='get_recommended_prep_strategy_display', read_only=True)

    class Meta:
        model = DailyForecastItem
        fields = [
            'id',
            'forecast_run',
            'menu_item',
            'menu_item_name',
            'chronos_prediction',
            'timesfm_prediction',
            'ensemble_prediction',
            'disagreement_score',
            'confidence_level',
            'confidence_level_display',
            'recommended_prep_strategy',
            'recommended_prep_strategy_display',
            'batch_1_portions',
            'batch_2_portions',
            'batch_3_portions',
        ]
        read_only_fields = [
            'id',
            'ensemble_prediction',
            'disagreement_score',
            'confidence_level',
            'recommended_prep_strategy',
            'batch_1_portions',
            'batch_2_portions',
            'batch_3_portions',
        ]


class KitchenPrepTargetSerializer(serializers.ModelSerializer):
    """Serializer for translated raw ingredient prep weights."""

    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    unit_of_measure = serializers.CharField(source='ingredient.unit_of_measure', read_only=True)

    class Meta:
        model = KitchenPrepTarget
        fields = [
            'id',
            'forecast_run',
            'ingredient',
            'ingredient_name',
            'unit_of_measure',
            'total_raw_qty_to_prep',
            'actual_used_qty',
            'variance_qty',
        ]
        read_only_fields = ['id', 'variance_qty']


class ForecastRunSerializer(serializers.ModelSerializer):
    """Summary serializer for forecast run records."""

    branch_name = serializers.CharField(source='branch.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_items_predicted = serializers.IntegerField(source='forecast_items.count', read_only=True)

    class Meta:
        model = ForecastRun
        fields = [
            'id',
            'branch',
            'branch_name',
            'forecast_target_date',
            'executed_at',
            'status',
            'status_display',
            'notes',
            'total_items_predicted',
        ]
        read_only_fields = ['id', 'executed_at']


class ForecastRunDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for forecast run, including nested items and prep targets."""

    branch_name = serializers.CharField(source='branch.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    forecast_items = DailyForecastItemSerializer(many=True, read_only=True)
    prep_targets = KitchenPrepTargetSerializer(many=True, read_only=True)

    class Meta:
        model = ForecastRun
        fields = [
            'id',
            'branch',
            'branch_name',
            'forecast_target_date',
            'executed_at',
            'status',
            'status_display',
            'notes',
            'forecast_items',
            'prep_targets',
        ]
        read_only_fields = ['id', 'executed_at']


class ForecastDataItemSerializer(serializers.Serializer):
    """Input serializer for a single item within the trigger forecast payload."""

    menu_item = serializers.UUIDField(help_text='UUID of the MenuItem being predicted')
    chronos_prediction = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0'),
        help_text='Predicted portion count from Amazon Chronos-Bolt'
    )
    timesfm_prediction = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0'),
        help_text='Predicted portion count from Google TimesFM'
    )


class TriggerForecastSerializer(serializers.Serializer):
    """Input serializer to trigger predictive forecast ingestion and BOM prep translation."""

    branch = serializers.UUIDField(help_text='UUID of the Branch outlet')
    target_date = serializers.DateField(help_text='Date the forecast is targeted for (YYYY-MM-DD)')
    forecast_data = serializers.ListField(
        child=ForecastDataItemSerializer(),
        allow_empty=False,
        help_text='List of per-menu-item predictions from ML models'
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        help_text='Optional operational notes or pipeline telemetry'
    )
