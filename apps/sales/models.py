"""Models for the Sales Records application.

Stores daily and shift-level Point-of-Sale (POS) transaction summaries
per menu item to train and drive AI demand forecasting engines (Chronos-Bolt + TimesFM).
"""

import uuid

from django.db import models


class ShiftChoices(models.TextChoices):
    """Operational meal service shifts."""
    MORNING_LUNCH = 'morning_lunch', 'Morning / Lunch (8AM-3PM)'
    EVENING_DINNER = 'evening_dinner', 'Evening / Dinner (3PM-10PM)'
    FULL_DAY = 'full_day', 'Full Day'


class SalesRecord(models.Model):
    """Daily/shift POS sales feeding the forecast engine."""

    ShiftChoices = ShiftChoices

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(
        'organization.Branch',
        on_delete=models.CASCADE,
        related_name='sales_records',
        help_text='Branch outlet where transactions occurred',
    )
    menu_item = models.ForeignKey(
        'menu.MenuItem',
        on_delete=models.CASCADE,
        related_name='sales_records',
        help_text='Finished dish or beverage sold',
    )
    sale_date = models.DateField(help_text='Calendar date of sale transactions')
    shift = models.CharField(
        max_length=20,
        choices=ShiftChoices.choices,
        help_text='Operational shift window (Morning/Lunch, Evening/Dinner, Full Day)',
    )
    quantity_sold = models.PositiveIntegerField(
        help_text='Total item portion count sold during this shift'
    )
    total_revenue_naira = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Gross revenue earned in Nigerian Naira (₦)',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['branch', 'menu_item', 'sale_date', 'shift']
        ordering = ['-sale_date']
        verbose_name = 'Sales Record'
        verbose_name_plural = 'Sales Records'

    def __str__(self):
        item_name = getattr(self.menu_item, 'name', str(self.menu_item_id))
        branch_name = getattr(self.branch, 'name', str(self.branch_id))
        return f'{item_name} x{self.quantity_sold} @ {branch_name} ({self.sale_date})'
