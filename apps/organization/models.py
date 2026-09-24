import uuid
from django.db import models


class RestaurantChain(models.Model):
    """
    Represents a Quick Service Restaurant (QSR) chain operating in South-East Nigeria.
    
    Examples include 'Crunchies', 'Kilimanjaro', 'Chicken Republic'.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, help_text="Chain brand name, e.g. Crunchies, Kilimanjaro")
    headquarters_city = models.CharField(max_length=100, help_text="Primary administrative city for chain headquarters")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Restaurant Chain'
        verbose_name_plural = 'Restaurant Chains'
        ordering = ['name']

    def __str__(self):
        return self.name


class Branch(models.Model):
    """
    Represents an individual physical restaurant outlet / branch belonging to a chain.
    """

    class CityChoices(models.TextChoices):
        ENUGU = 'ENUGU', 'Enugu'
        AWKA = 'AWKA', 'Awka'
        OWERRI = 'OWERRI', 'Owerri'
        ABAKALIKI = 'ABAKALIKI', 'Abakaliki'
        UMUAHIA = 'UMUAHIA', 'Umuahia'
        ONITSHA = 'ONITSHA', 'Onitsha'
        ABA = 'ABA', 'Aba'

    class StateChoices(models.TextChoices):
        ENUGU = 'ENUGU', 'Enugu'
        ANAMBRA = 'ANAMBRA', 'Anambra'
        IMO = 'IMO', 'Imo'
        EBONYI = 'EBONYI', 'Ebonyi'
        ABIA = 'ABIA', 'Abia'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chain = models.ForeignKey(
        RestaurantChain,
        on_delete=models.CASCADE,
        related_name='branches',
        help_text="Parent QSR brand"
    )
    name = models.CharField(max_length=150, help_text="Branch name, e.g. Enugu Ogui Road, Awka Aroma")
    city = models.CharField(
        max_length=50,
        choices=CityChoices.choices,
        help_text="South-East Nigerian operational city"
    )
    state = models.CharField(
        max_length=50,
        choices=StateChoices.choices,
        help_text="State in South-East Nigeria"
    )
    address = models.TextField(blank=True, help_text="Street address of the branch outlet")
    is_pilot_intervention = models.BooleanField(
        default=False,
        help_text="True = Treatment branch (utilizing AI waste reduction intervention), False = Control branch"
    )
    has_standby_generator = models.BooleanField(
        default=True,
        help_text="Indicates whether the branch possesses a functional backup power generator"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this branch is currently open and operating"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Branch'
        verbose_name_plural = 'Branches'
        unique_together = ['chain', 'name']
        ordering = ['chain', 'name']

    def __str__(self):
        return f'{self.chain.name} - {self.name} ({self.city})'
