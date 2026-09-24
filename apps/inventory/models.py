"""Inventory models for Smart Food-Waste Reduction Framework.

Tracks raw ingredient batches using First-Expired-First-Out (FEFO) inventory
management and logs power grid/generator outages affecting cold chain integrity
across branch outlets in South-East Nigeria.
"""

import uuid
from django.db import models


class StorageType(models.TextChoices):
    """Storage temperature conditions for inventory batches."""
    CHILLED = 'chilled', 'Chilled'
    AMBIENT = 'ambient', 'Ambient'
    FROZEN = 'frozen', 'Frozen'


class InventoryBatch(models.Model):
    """A specific received lot or batch of a raw ingredient at an outlet branch."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(
        'organization.Branch',
        on_delete=models.CASCADE,
        related_name='inventory_batches',
        help_text='Branch outlet holding this batch'
    )
    ingredient = models.ForeignKey(
        'menu.Ingredient',
        on_delete=models.CASCADE,
        related_name='inventory_batches',
        help_text='Ingredient type for this batch'
    )
    quantity_received = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Total quantity received upon delivery'
    )
    quantity_remaining = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Current remaining quantity available for cooking'
    )
    unit_cost_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Cost per unit paid at time of purchase in Naira (₦)'
    )
    received_date = models.DateField(
        help_text='Date this batch was delivered and received'
    )
    expiry_date = models.DateField(
        help_text='Expiration date calculated from shelf life and storage conditions'
    )
    storage_type = models.CharField(
        max_length=20,
        choices=StorageType.choices,
        help_text='Storage method (chilled, ambient, frozen)'
    )
    is_depleted = models.BooleanField(
        default=False,
        help_text='Flag indicating whether batch has been fully consumed or discarded'
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional notes regarding batch quality, supplier, or delivery condition'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Inventory Batch'
        verbose_name_plural = 'Inventory Batches'
        ordering = ['expiry_date']  # FEFO (First-Expired, First-Out) ordering

    def __str__(self):
        return f'{self.ingredient.name} @ {self.branch.name} (Expires: {self.expiry_date})'


class PowerOutageLog(models.Model):
    """Records power grid and generator failures affecting refrigeration cold chains."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(
        'organization.Branch',
        on_delete=models.CASCADE,
        related_name='power_outage_logs',
        help_text='Branch outlet experiencing the outage'
    )
    outage_start = models.DateTimeField(
        help_text='Timestamp when power failure began'
    )
    outage_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when power was restored (grid or generator)'
    )
    generator_available = models.BooleanField(
        default=False,
        help_text='Whether a standby generator was operational during the outage'
    )
    notes = models.TextField(
        blank=True,
        help_text='Details on chiller temperatures, food safety checks, or fuel shortages'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Power Outage Log'
        verbose_name_plural = 'Power Outage Logs'
        ordering = ['-outage_start']

    @property
    def duration_hours(self):
        """Calculate outage duration in hours if outage has ended."""
        if self.outage_end and self.outage_start:
            return round((self.outage_end - self.outage_start).total_seconds() / 3600.0, 2)
        return None

    def __str__(self):
        start_str = self.outage_start.strftime("%Y-%m-%d %H:%M") if self.outage_start else "N/A"
        return f'Outage at {self.branch.name} ({start_str})'
