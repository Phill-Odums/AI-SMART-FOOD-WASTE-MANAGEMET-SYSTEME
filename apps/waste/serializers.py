"""Serializers for Waste Tracking application."""

from rest_framework import serializers

from .models import WasteLog


class WasteLogSerializer(serializers.ModelSerializer):
    """Full detail and create/update serializer for individual waste logs."""

    class Meta:
        model = WasteLog
        fields = [
            'id',
            'branch',
            'logged_by',
            'timestamp',
            'operational_stage',
            'menu_item',
            'ingredient',
            'weight_kg',
            'financial_loss_naira',
            'root_cause_determinant',
            'notes',
        ]
        read_only_fields = ['id', 'timestamp', 'financial_loss_naira']


class WasteLogListSerializer(serializers.ModelSerializer):
    """Optimized list serializer including related entity names."""

    branch_name = serializers.CharField(source='branch.name', read_only=True)
    logged_by_name = serializers.SerializerMethodField(read_only=True)
    menu_item_name = serializers.CharField(
        source='menu_item.name', read_only=True, default=None
    )
    ingredient_name = serializers.CharField(
        source='ingredient.name', read_only=True, default=None
    )

    class Meta:
        model = WasteLog
        fields = [
            'id',
            'branch',
            'branch_name',
            'logged_by',
            'logged_by_name',
            'timestamp',
            'operational_stage',
            'menu_item',
            'menu_item_name',
            'ingredient',
            'ingredient_name',
            'weight_kg',
            'financial_loss_naira',
            'root_cause_determinant',
            'notes',
        ]
        read_only_fields = [
            'id',
            'timestamp',
            'financial_loss_naira',
            'branch_name',
            'logged_by_name',
            'menu_item_name',
            'ingredient_name',
        ]

    def get_logged_by_name(self, obj) -> str | None:
        """Derive staff member's full name or username."""
        if obj.logged_by:
            user = getattr(obj.logged_by, 'user', None)
            if user:
                full_name = user.get_full_name()
                return full_name if full_name else getattr(user, 'username', str(user))
            return str(obj.logged_by)
        return None


class WasteDailySummarySerializer(serializers.Serializer):
    """Summary aggregation serializer for daily waste metrics per branch."""

    date = serializers.DateField(help_text='Calendar date for waste aggregation')
    total_weight_kg = serializers.DecimalField(
        max_digits=12,
        decimal_places=3,
        help_text='Total food waste discarded in kg',
    )
    total_loss_naira = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text='Total estimated financial loss in ₦',
    )
    count = serializers.IntegerField(
        help_text='Total number of waste events recorded'
    )
    breakdown_by_stage = serializers.DictField(
        help_text='Dictionary breakdown of waste metrics partitioned by operational stage'
    )
