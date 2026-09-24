"""Models for the Local Calendar Context application.

Encapsulates South-East Nigerian contextual variables such as Igbo 4-day market
cycles (Eke, Oye, Afor, Nkwo), civil service payday windows, Sunday church surges,
and seasonal weather states to enrich demand forecasting and waste reduction models.
"""

import datetime
import uuid

from django.db import models


class CityChoices(models.TextChoices):
    """South-East Nigerian urban commercial centers."""
    ENUGU = 'ENUGU', 'Enugu'
    AWKA = 'AWKA', 'Awka'
    OWERRI = 'OWERRI', 'Owerri'
    ABAKALIKI = 'ABAKALIKI', 'Abakaliki'
    UMUAHIA = 'UMUAHIA', 'Umuahia'
    ONITSHA = 'ONITSHA', 'Onitsha'
    ABA = 'ABA', 'Aba'


class TraditionalMarketDay(models.TextChoices):
    """Igbo four-day market cycle identifiers."""
    NONE = 'none', 'None'
    EKE = 'eke', 'Eke'
    OYE = 'oye', 'Oye'
    AFOR = 'afor', 'Afor'
    NKWO = 'nkwo', 'Nkwo'


class WeatherFlag(models.TextChoices):
    """Weather and meteorological classifications."""
    SUNNY = 'sunny', 'Sunny'
    RAINY_AFTERNOON = 'rainy_afternoon', 'Rainy Afternoon'
    HEAVY_DOWNPOUR = 'heavy_downpour', 'Heavy Downpour'
    HARMATTAN = 'harmattan', 'Harmattan'


class LocalCalendarContext(models.Model):
    """Daily contextual calendar features for a South-East Nigerian city."""

    TraditionalMarketDay = TraditionalMarketDay
    WeatherFlag = WeatherFlag
    CityChoices = CityChoices

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(help_text='Calendar date')
    city = models.CharField(
        max_length=50,
        choices=CityChoices.choices,
        help_text='Target urban center in South-East Nigeria',
    )
    traditional_market_day = models.CharField(
        max_length=10,
        choices=TraditionalMarketDay.choices,
        default=TraditionalMarketDay.NONE,
        help_text='Igbo traditional 4-day market name (Eke, Oye, Afor, Nkwo)',
    )
    is_major_market_day = models.BooleanField(
        default=False,
        help_text='True if this market day is significant for this particular city',
    )
    is_payday_window = models.BooleanField(
        default=False,
        help_text='True if date falls within civil service/corporate salary window (25th-31st)',
    )
    is_sunday_church_surge = models.BooleanField(
        default=False,
        help_text='True if date falls on a Sunday with heightened post-service restaurant dining',
    )
    is_public_holiday = models.BooleanField(
        default=False,
        help_text='True if date is a recognized national or state public holiday',
    )
    public_holiday_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Name of observed holiday, e.g. Workers Day, Christmas Day',
    )
    weather_flag = models.CharField(
        max_length=20,
        choices=WeatherFlag.choices,
        default=WeatherFlag.SUNNY,
        help_text='Expected or recorded prevailing weather condition',
    )
    custom_event_note = models.TextField(
        blank=True,
        help_text='E.g. University graduation week, local festival, gubernatorial election',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['date', 'city']
        ordering = ['-date']
        verbose_name = 'Local Calendar Context'
        verbose_name_plural = 'Local Calendar Contexts'

    def __str__(self):
        return f'{self.city} - {self.date} ({self.get_traditional_market_day_display()})'

    @classmethod
    def compute_market_day(cls, target_date: datetime.date | datetime.datetime) -> str:
        """Calculate the Igbo traditional market day for any given date.

        Reference epoch: January 1, 2024 was an Eke day.
        The 4-day cycle is: Eke(0) -> Oye(1) -> Afor(2) -> Nkwo(3).
        """
        if isinstance(target_date, datetime.datetime):
            target_date = target_date.date()

        epoch = datetime.date(2024, 1, 1)  # Eke
        days_since_epoch = (target_date - epoch).days
        index = days_since_epoch % 4

        cycle_map = {
            0: TraditionalMarketDay.EKE,
            1: TraditionalMarketDay.OYE,
            2: TraditionalMarketDay.AFOR,
            3: TraditionalMarketDay.NKWO,
        }
        return cycle_map.get(index, TraditionalMarketDay.NONE)

    @classmethod
    def is_city_major_market(cls, city: str, market_day: str) -> bool:
        """Determine if a market day is traditionally significant for the given city."""
        c = str(city).upper()
        m = str(market_day).lower()

        # Traditional high-volume city market alignments in SE Nigeria
        if 'AWKA' in c and m == TraditionalMarketDay.EKE:
            return True
        if 'OWERRI' in c and m == TraditionalMarketDay.EKE:
            return True
        if 'ONITSHA' in c and m in (TraditionalMarketDay.NKWO, TraditionalMarketDay.OYE):
            return True
        if 'ABA' in c and m in (TraditionalMarketDay.EKE, TraditionalMarketDay.NKWO):
            return True
        if 'ABAKALIKI' in c and m in (TraditionalMarketDay.AFOR, TraditionalMarketDay.NKWO):
            return True
        return False

    def save(self, *args, **kwargs):
        """Auto-compute payday, Sunday surge, and traditional market day features."""
        if self.date:
            if self.date.day >= 25:
                self.is_payday_window = True
            if self.date.weekday() == 6:  # Sunday
                self.is_sunday_church_surge = True
            if not self.traditional_market_day or self.traditional_market_day == TraditionalMarketDay.NONE:
                self.traditional_market_day = self.compute_market_day(self.date)
            if not self.is_major_market_day:
                self.is_major_market_day = self.is_city_major_market(self.city, self.traditional_market_day)

        super().save(*args, **kwargs)
