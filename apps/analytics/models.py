"""Models for the Analytics application.

Provides periodic menu engineering snapshots (Star, Plowhorse, Puzzle, Dog)
and pilot KPI tracking for pre vs. post quasi-experimental intervention analysis.
"""

from decimal import Decimal, ROUND_HALF_UP
import uuid

from django.db import models


class MenuEngineeringSnapshot(models.Model):
    """Periodic analysis of menu item sales popularity vs food waste generation."""

    class MatrixCategory(models.TextChoices):
        STAR = 'star', 'Star (High Profit, Low Waste)'
        PLOWHORSE = 'plowhorse', 'Plowhorse (High Sales, Low Profit)'
        PUZZLE = 'puzzle', 'Puzzle (Low Sales, High Profit)'
        DOG = 'dog', 'Dog (Low Sales, Low Profit, High Waste)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(
        'organization.Branch',
        on_delete=models.CASCADE,
        related_name='menu_snapshots',
        help_text='Branch outlet where analysis was evaluated'
    )
    menu_item = models.ForeignKey(
        'menu.MenuItem',
        on_delete=models.CASCADE,
        related_name='engineering_snapshots',
        help_text='Menu dish evaluated'
    )
    period_start = models.DateField(
        help_text='Start date of the observation period'
    )
    period_end = models.DateField(
        help_text='End date of the observation period'
    )
    units_sold = models.PositiveIntegerField(
        default=0,
        help_text='Total customer portions sold during period'
    )
    waste_weight_kg = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        help_text='Total waste mass discarded in kilograms'
    )
    waste_cost_naira = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Financial value lost to food waste in Nigerian Naira (₦)'
    )
    revenue_naira = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Gross sales revenue earned in Nigerian Naira (₦)'
    )
    ingredient_cost_naira = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Total raw ingredient cost calculated from Recipe BOM'
    )
    profit_margin_naira = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Gross margin: revenue - ingredient cost'
    )
    matrix_category = models.CharField(
        max_length=15,
        choices=MatrixCategory.choices,
        help_text='Menu engineering quadrant classification'
    )
    recommendation = models.TextField(
        blank=True,
        help_text='Prescriptive operational recommendation for kitchen and management'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Snapshot generation timestamp'
    )

    class Meta:
        ordering = ['-period_end']
        unique_together = ['branch', 'menu_item', 'period_start', 'period_end']
        verbose_name = 'Menu Engineering Snapshot'
        verbose_name_plural = 'Menu Engineering Snapshots'

    def __str__(self):
        item_name = getattr(self.menu_item, 'name', str(self.menu_item_id))
        branch_name = getattr(self.branch, 'name', str(self.branch_id))
        return f'{item_name} @ {branch_name}: {self.get_matrix_category_display()} ({self.period_start} to {self.period_end})'


class PilotKPISnapshot(models.Model):
    """Tracks pre- and post-intervention operational KPIs for the quasi-experiment."""

    class PeriodLabel(models.TextChoices):
        PRE_INTERVENTION = 'pre_intervention', 'Pre-Intervention'
        POST_INTERVENTION = 'post_intervention', 'Post-Intervention'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(
        'organization.Branch',
        on_delete=models.CASCADE,
        related_name='pilot_kpis',
        help_text='Branch outlet evaluated'
    )
    snapshot_date = models.DateField(
        help_text='Date this KPI snapshot summarizes'
    )
    period_label = models.CharField(
        max_length=20,
        choices=PeriodLabel.choices,
        help_text='Research trial phase: baseline pre-intervention vs AI post-intervention'
    )
    total_waste_kg = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        help_text='Total aggregate food waste generated in kilograms'
    )
    total_waste_cost_naira = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Total monetary loss from discarded food in Nigerian Naira (₦)'
    )
    total_sales_revenue_naira = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Total sales revenue in Nigerian Naira (₦)'
    )
    waste_to_revenue_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal('0.0000'),
        help_text='waste_cost / revenue ratio'
    )
    forecast_accuracy_mape = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Mean Absolute Percentage Error of forecast'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when snapshot record was logged'
    )

    class Meta:
        ordering = ['-snapshot_date']
        unique_together = ['branch', 'snapshot_date', 'period_label']
        verbose_name = 'Pilot KPI Snapshot'
        verbose_name_plural = 'Pilot KPI Snapshots'

    def __str__(self):
        branch_name = getattr(self.branch, 'name', str(self.branch_id))
        return f'{branch_name} - {self.get_period_label_display()} ({self.snapshot_date})'

    def save(self, *args, **kwargs):
        """Auto-calculate waste_to_revenue_ratio if revenue > 0."""
        if self.total_sales_revenue_naira and Decimal(str(self.total_sales_revenue_naira)) > Decimal('0'):
            ratio = Decimal(str(self.total_waste_cost_naira)) / Decimal(str(self.total_sales_revenue_naira))
            self.waste_to_revenue_ratio = ratio.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        else:
            self.waste_to_revenue_ratio = Decimal('0.0000')
        super().save(*args, **kwargs)
