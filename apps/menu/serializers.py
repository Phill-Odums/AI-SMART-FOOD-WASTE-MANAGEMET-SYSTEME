"""Serializers for Menu app models: Ingredient, MenuItem, and RecipeBOM."""

from rest_framework import serializers
from .models import Ingredient, MenuItem, RecipeBOM


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for raw ingredients."""

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class MenuItemSerializer(serializers.ModelSerializer):
    """Standard serializer for finished menu items."""

    class Meta:
        model = MenuItem
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class RecipeBOMSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Recipe Bill of Materials entries."""

    class Meta:
        model = RecipeBOM
        fields = '__all__'
        read_only_fields = ['id']


class RecipeBOMDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Recipe Bill of Materials with resolved names."""
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    ingredient_unit = serializers.CharField(source='ingredient.unit_of_measure', read_only=True)

    class Meta:
        model = RecipeBOM
        fields = [
            'id',
            'menu_item',
            'menu_item_name',
            'ingredient',
            'ingredient_name',
            'ingredient_unit',
            'quantity_required',
            'prep_yield_loss_pct',
        ]
        read_only_fields = ['id', 'ingredient_name', 'menu_item_name', 'ingredient_unit']


class MenuItemDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for MenuItem including nested recipe bill of materials."""
    bom_items = RecipeBOMDetailSerializer(many=True, read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            'id',
            'chain',
            'name',
            'category',
            'selling_price_naira',
            'is_perishable_daily',
            'is_active',
            'bom_items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'bom_items']
