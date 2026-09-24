"""Models for the Waste Tracking application.

Tracks edible and preparation food waste across operational stages in
South-East Nigerian QSR outlets.
"""

from decimal import Decimal
import uuid

from django.db import models


class WasteLog(models.Model):
    """Records individual waste disposal events across kitchen and service stages."""

    class OperationalStage(models.TextChoices):
        PREPARATION = 'preparation', 'Preparation & Cooking'
        STORAGE_SPOILAGE = 'storage_spoilage', 'Storage & Spoilage'
        OVERPRODUCTION_BUFFET = 'overproduction_buffet', 'Overproduction & Buffet'
        PLATE_WASTE = 'plate_waste', 'Customer Plate Waste'

    class RootCauseDeterminant(models.TextChoices):
        POWER_OUTAGE_SPOILAGE = 'power_outage_spoilage', 'Power Outage / Spoilage'
        OVERCOOKED_BURNT = 'overcooked_burnt', 'Overcooked / Burnt'
        EXPIRED_IN_STORE = 'expired_in_store', 'Expired in Storage'
        OVERPRODUCED_UNSOLD = 'overproduced_unsold', 'Overproduced / Unsold'
        CUSTOMER_LEFTOVER = 'customer_leftover', 'Customer Leftover'
        TRIMMING_EXCESS = 'trimming_excess', 'Trimming / Peeling Excess'
        OTHER = 'other', 'Other'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(
        'organization.Branch',
        on_delete=models.CASCADE,
        related_name='waste_logs',
        help_text='Branch outlet where waste occurred',
    )
    logged_by = models.ForeignKey(
        'accounts.UserProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='waste_logs',
        help_text='Staff member logging the waste entry',
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    operational_stage = models.CharField(
        max_length=30,
        choices=OperationalStage.choices,
        help_text='Stage in restaurant lifecycle where waste was generated',
    )
    menu_item = models.ForeignKey(
        'menu.MenuItem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='waste_logs',
        help_text='If discarded item was a cooked dish',
    )
    ingredient = models.ForeignKey(
        'menu.Ingredient',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='waste_logs',
        help_text='If discarded item was a raw ingredient',
    )
    weight_kg = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        help_text='Measured weight of discarded food in kilograms',
    )
    financial_loss_naira = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Auto-calculated from weight and unit cost',
    )
    root_cause_determinant = models.CharField(
        max_length=30,
        choices=RootCauseDeterminant.choices,
        help_text='Primary driver or trigger for waste event',
    )
    notes = models.TextField(blank=True, help_text='Additional context or remarks')

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Waste Log'
        verbose_name_plural = 'Waste Logs'

    def __str__(self):
        branch_name = getattr(self.branch, 'name', str(self.branch_id))
        return f'Waste: {self.weight_kg}kg at {branch_name} ({self.get_operational_stage_display()})'

    def save(self, *args, **kwargs):
        """Auto-calculate financial_loss_naira if not explicitly set."""
        if self.financial_loss_naira is None or self.financial_loss_naira == Decimal('0.00'):
            computed_loss = Decimal('0.00')
            weight = Decimal(str(self.weight_kg)) if self.weight_kg is not None else Decimal('0.00')

            if self.ingredient_id:
                try:
                    from apps.menu.models import Ingredient
                    ing = self.ingredient or Ingredient.objects.filter(pk=self.ingredient_id).first()
                    if ing and hasattr(ing, 'unit_cost_naira') and ing.unit_cost_naira is not None:
                        computed_loss = weight * Decimal(str(ing.unit_cost_naira))
                except Exception:
                    pass
            elif self.menu_item_id:
                try:
                    from apps.menu.models import MenuItem
                    item = self.menu_item or MenuItem.objects.filter(pk=self.menu_item_id).first()
                    if item and hasattr(item, 'selling_price_naira') and item.selling_price_naira is not None:
                        # Rough proxy based on menu item selling price
                        computed_loss = weight * Decimal(str(item.selling_price_naira))
                except Exception:
                    pass

            self.financial_loss_naira = round(computed_loss, 2)

        super().save(*args, **kwargs)
