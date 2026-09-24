"""Menu and Recipe models for Smart Food-Waste Reduction Framework.

Manages raw ingredients, finished menu items, and Recipe Bill of Materials (BOM)
for QSR chains operating in South-East Nigeria.
"""

import uuid
from django.db import models


class UnitOfMeasure(models.TextChoices):
    """Measurement units for raw kitchen ingredients."""
    KG = 'kg', 'kg'
    GRAM = 'gram', 'gram'
    LITRE = 'litre', 'litre'
    PIECE = 'piece', 'piece'


class MenuCategory(models.TextChoices):
    """Category classification for finished dishes sold to customers."""
    MAIN_RICE = 'main_rice', 'Main Rice'
    PROTEIN = 'protein', 'Protein'
    SIDES = 'sides', 'Sides'
    SWALLOW_SOUP = 'swallow_soup', 'Swallow & Soup'
    PASTA = 'pasta', 'Pasta'
    BEVERAGE = 'beverage', 'Beverage'
    SNACK = 'snack', 'Snack'


class Ingredient(models.Model):
    """Raw perishable or commodity item used in restaurant food preparation."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chain = models.ForeignKey(
        'organization.RestaurantChain',
        on_delete=models.CASCADE,
        related_name='ingredients',
        help_text='The restaurant chain owning this ingredient specification'
    )
    name = models.CharField(
        max_length=100,
        help_text="Ingredient name, e.g. 'Parboiled Rice', 'Fresh Whole Chicken', 'Vegetable Oil'"
    )
    unit_of_measure = models.CharField(
        max_length=10,
        choices=UnitOfMeasure.choices,
        help_text='Standard unit of measure for inventory and recipe portions'
    )
    unit_cost_naira = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Current cost per unit in Nigerian Naira (₦)'
    )
    shelf_life_days_chilled = models.PositiveIntegerField(
        help_text='Days usable under refrigeration'
    )
    shelf_life_days_ambient = models.PositiveIntegerField(
        help_text='Days usable at room temperature'
    )
    minimum_reorder_level = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Threshold quantity to trigger stock replenishment'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this ingredient is currently in active operational use'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        unique_together = ['chain', 'name']
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_unit_of_measure_display()})'


class MenuItem(models.Model):
    """Finished culinary dish sold directly to QSR customers."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chain = models.ForeignKey(
        'organization.RestaurantChain',
        on_delete=models.CASCADE,
        related_name='menu_items',
        help_text='The restaurant chain offering this menu item'
    )
    name = models.CharField(
        max_length=150,
        help_text="Menu item name, e.g. 'Jollof Rice Standard', 'Fried Chicken 1-Piece'"
    )
    category = models.CharField(
        max_length=30,
        choices=MenuCategory.choices,
        help_text='Menu category for operational classification'
    )
    selling_price_naira = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Retail price to customers in Nigerian Naira (₦)'
    )
    is_perishable_daily = models.BooleanField(
        default=True,
        help_text='Must unsold cooked food be discarded at closing?'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this menu item is currently offered'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        unique_together = ['chain', 'name']
        ordering = ['name']

    def __str__(self):
        return f'{self.name} (₦{self.selling_price_naira})'


class RecipeBOM(models.Model):
    """Bill of Materials linking a finished MenuItem to its required raw Ingredients."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        related_name='bom_items',
        help_text='Finished menu item dish'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='used_in_recipes',
        help_text='Raw ingredient constituent'
    )
    quantity_required = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text='Qty of ingredient per 1 portion'
    )
    prep_yield_loss_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Normal cooking/prep shrinkage %'
    )

    class Meta:
        verbose_name = 'Recipe Bill of Materials'
        verbose_name_plural = 'Recipe Bills of Materials'
        unique_together = ['menu_item', 'ingredient']
        ordering = ['menu_item', 'ingredient']

    def __str__(self):
        return f'{self.menu_item.name} <- {self.ingredient.name} ({self.quantity_required} {self.ingredient.unit_of_measure})'
