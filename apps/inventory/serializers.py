"""Serializers for Inventory app models: InventoryBatch and PowerOutageLog."""

from django.utils import timezone
from rest_framework import serializers

from .models import InventoryBatch, PowerOutageLog


class InventoryBatchSerializer(serializers.ModelSerializer):
    """Standard serializer for raw ingredient inventory batches."""

    class Meta:
        model = InventoryBatch
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class InventoryBatchListSerializer(serializers.ModelSerializer):
    """List serializer for Inventory batches with FEFO context and computed days until expiry."""
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    days_until_expiry = serializers.SerializerMethodField()

    class Meta:
        model = InventoryBatch
        fields = [
            'id',
            'branch',
            'branch_name',
            'ingredient',
            'ingredient_name',
            'quantity_received',
            'quantity_remaining',
            'unit_cost_at_purchase',
            'received_date',
            'expiry_date',
            'storage_type',
            'is_depleted',
            'notes',
            'days_until_expiry',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'ingredient_name',
            'branch_name',
            'days_until_expiry',
        ]

    def get_days_until_expiry(self, obj):
        """Calculate days remaining until batch expiration."""
        if obj.expiry_date:
            today = timezone.now().date()
            return (obj.expiry_date - today).days
        return None


class PowerOutageLogSerializer(serializers.ModelSerializer):
    """Serializer for power outage and generator operational logs."""
    duration_hours = serializers.FloatField(read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = PowerOutageLog
        fields = [
            'id',
            'branch',
            'branch_name',
            'outage_start',
            'outage_end',
            'generator_available',
            'notes',
            'duration_hours',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'duration_hours', 'branch_name']
