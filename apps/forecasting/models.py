"""Models for the AI Demand Forecasting application.

Stores execution metadata for foundation-model forecast runs (Chronos-Bolt + TimesFM),
per-item blended predictions with disagreement-based batching recommendations,
and translated kitchen raw-ingredient preparation targets.
"""

from decimal import Decimal, ROUND_HALF_UP
import uuid

from django.db import models


class ForecastRun(models.Model):
    """Execution record for a daily predictive demand forecasting job."""

    class Status(models.TextChoices):
        SUCCESS = 'success', 'Success'
        PARTIAL_FALLBACK = 'partial_fallback', 'Partial (Single Model Fallback)'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(
        'organization.Branch',
        on_delete=models.CASCADE,
        related_name='forecast_runs',
        help_text='Branch outlet for which the forecast was computed'
    )
    forecast_target_date = models.DateField(
        help_text='The date this forecast predicts for'
    )
    executed_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when the forecasting engine executed'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUCCESS,
        help_text='Operational status of this predictive run'
    )
    notes = models.TextField(
        blank=True,
        help_text='System logs, error traces, or operational notes'
    )

    class Meta:
        ordering = ['-executed_at']
        unique_together = ['branch', 'forecast_target_date']
        verbose_name = 'Forecast Run'
        verbose_name_plural = 'Forecast Runs'

    def __str__(self):
        branch_name = getattr(self.branch, 'name', str(self.branch_id))
        return f'Forecast for {branch_name} on {self.forecast_target_date} ({self.get_status_display()})'


class DailyForecastItem(models.Model):
    """Ensemble prediction and production batching recommendation for a specific menu item."""

    class ConfidenceLevel(models.TextChoices):
        HIGH = 'high', 'High'
        LOW = 'low', 'Low'

    class PrepStrategy(models.TextChoices):
        SINGLE_BULK_BATCH = 'single_bulk_batch', 'Single Bulk Batch'
        TWO_STAGGERED_BATCHES = 'two_staggered_batches', 'Two Staggered Batches'
        THREE_BATCHES = 'three_batches', 'Three Batches'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    forecast_run = models.ForeignKey(
        ForecastRun,
        on_delete=models.CASCADE,
        related_name='forecast_items',
        help_text='Associated daily forecasting execution'
    )
    menu_item = models.ForeignKey(
        'menu.MenuItem',
        on_delete=models.CASCADE,
        related_name='forecast_items',
        help_text='Target finished dish being predicted'
    )
    chronos_prediction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Portions predicted by Amazon Chronos-Bolt'
    )
    timesfm_prediction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Portions predicted by Google TimesFM'
    )
    ensemble_prediction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Blended forecast'
    )
    disagreement_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Absolute divergence between models'
    )
    confidence_level = models.CharField(
        max_length=10,
        choices=ConfidenceLevel.choices,
        help_text='High agreement (<8% divergence) vs Low agreement'
    )
    recommended_prep_strategy = models.CharField(
        max_length=30,
        choices=PrepStrategy.choices,
        help_text='Dynamic kitchen batching strategy to avert overproduction waste'
    )
    batch_1_portions = models.PositiveIntegerField(
        default=0,
        help_text='Portions allocated to initial morning/lunch prep batch'
    )
    batch_2_portions = models.PositiveIntegerField(
        default=0,
        help_text='Portions reserved for top-up afternoon batch if demand manifests'
    )
    batch_3_portions = models.PositiveIntegerField(
        default=0,
        help_text='Portions reserved for tertiary batch'
    )

    class Meta:
        unique_together = ['forecast_run', 'menu_item']
        ordering = ['menu_item__name']
        verbose_name = 'Daily Forecast Item'
        verbose_name_plural = 'Daily Forecast Items'

    def __str__(self):
        item_name = getattr(self.menu_item, 'name', str(self.menu_item_id))
        return f'{item_name}: {self.ensemble_prediction} portions ({self.get_confidence_level_display()} confidence)'

    def save(self, *args, **kwargs):
        """Auto-calculate ensemble, divergence score, confidence, and batch sizes."""
        if self.chronos_prediction is not None and self.timesfm_prediction is not None:
            c = Decimal(str(self.chronos_prediction))
            t = Decimal(str(self.timesfm_prediction))
            ensemble = ((c + t) / Decimal('2')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            disagreement = abs(c - t).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.ensemble_prediction = ensemble
            self.disagreement_score = disagreement

            if ensemble > Decimal('0'):
                divergence_ratio = disagreement / ensemble
            else:
                divergence_ratio = Decimal('0')

            # Divergence threshold: 8% (0.08)
            if divergence_ratio < Decimal('0.08'):
                self.confidence_level = self.ConfidenceLevel.HIGH
                self.recommended_prep_strategy = self.PrepStrategy.SINGLE_BULK_BATCH
                self.batch_1_portions = int(round(float(ensemble)))
                self.batch_2_portions = 0
                self.batch_3_portions = 0
            else:
                self.confidence_level = self.ConfidenceLevel.LOW
                self.recommended_prep_strategy = self.PrepStrategy.TWO_STAGGERED_BATCHES
                self.batch_1_portions = int(round(float(ensemble) * 0.65))
                self.batch_2_portions = int(round(float(ensemble) * 0.35))
                self.batch_3_portions = 0

        super().save(*args, **kwargs)


class KitchenPrepTarget(models.Model):
    """Raw ingredient quantity targets translated from portion forecasts via Recipe BOM."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    forecast_run = models.ForeignKey(
        ForecastRun,
        on_delete=models.CASCADE,
        related_name='prep_targets',
        help_text='Associated forecast run'
    )
    ingredient = models.ForeignKey(
        'menu.Ingredient',
        on_delete=models.CASCADE,
        related_name='prep_targets',
        help_text='Raw ingredient constituent'
    )
    total_raw_qty_to_prep = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        help_text='Total raw ingredient quantity calculated via Recipe BOM'
    )
    actual_used_qty = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text='Filled by cook at end of shift'
    )
    variance_qty = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text='Difference: recommended vs actual'
    )

    class Meta:
        unique_together = ['forecast_run', 'ingredient']
        ordering = ['ingredient__name']
        verbose_name = 'Kitchen Prep Target'
        verbose_name_plural = 'Kitchen Prep Targets'

    def __str__(self):
        ingredient_name = getattr(self.ingredient, 'name', str(self.ingredient_id))
        uom = getattr(self.ingredient, 'unit_of_measure', '')
        return f'{ingredient_name}: Prep {self.total_raw_qty_to_prep} {uom}'

    def save(self, *args, **kwargs):
        """Auto-calculate variance if actual_used_qty is entered."""
        if self.actual_used_qty is not None and self.total_raw_qty_to_prep is not None:
            self.variance_qty = (
                Decimal(str(self.actual_used_qty)) - Decimal(str(self.total_raw_qty_to_prep))
            ).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)
