"""Django Admin configuration for Menu app."""

from django.contrib import admin
from .models import Ingredient, MenuItem, RecipeBOM


class RecipeBOMInline(admin.TabularInline):
    """Inline view of Recipe BOM items within the MenuItem admin change form."""
    model = RecipeBOM
    extra = 1
    autocomplete_fields = ['ingredient']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Admin configuration for raw ingredients."""
    list_display = [
        'name',
        'chain',
        'unit_of_measure',
        'unit_cost_naira',
        'shelf_life_days_chilled',
        'shelf_life_days_ambient',
        'minimum_reorder_level',
        'is_active',
        'created_at',
    ]
    list_filter = ['chain', 'unit_of_measure', 'is_active']
    search_fields = ['name', 'chain__name']
    ordering = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """Admin configuration for finished menu items."""
    list_display = [
        'name',
        'chain',
        'category',
        'selling_price_naira',
        'is_perishable_daily',
        'is_active',
        'created_at',
    ]
    list_filter = ['chain', 'category', 'is_perishable_daily', 'is_active']
    search_fields = ['name', 'chain__name']
    ordering = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [RecipeBOMInline]


@admin.register(RecipeBOM)
class RecipeBOMAdmin(admin.ModelAdmin):
    """Admin configuration for Recipe Bill of Materials."""
    list_display = [
        'menu_item',
        'ingredient',
        'quantity_required',
        'prep_yield_loss_pct',
    ]
    list_filter = ['menu_item__chain', 'ingredient__chain']
    search_fields = ['menu_item__name', 'ingredient__name']
    ordering = ['menu_item', 'ingredient']
    readonly_fields = ['id']
