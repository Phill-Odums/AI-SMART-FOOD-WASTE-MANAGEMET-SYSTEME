import uuid
from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """
    Extends the base user model with branch affiliation and operational roles
    for the food waste reduction platform.
    """

    class RoleChoices(models.TextChoices):
        KITCHEN_COOK = 'kitchen_cook', 'Kitchen Cook'
        STORE_KEEPER = 'store_keeper', 'Store Keeper'
        BRANCH_MANAGER = 'branch_manager', 'Branch Manager'
        AREA_MANAGER = 'area_manager', 'Area Manager'
        RESEARCH_AUDITOR = 'research_auditor', 'Research Auditor'
        ADMIN = 'admin', 'Admin'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="Underlying Django auth user"
    )
    branch = models.ForeignKey(
        'organization.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff',
        help_text="Assigned physical restaurant branch"
    )
    role = models.CharField(
        max_length=30,
        choices=RoleChoices.choices,
        default=RoleChoices.KITCHEN_COOK,
        help_text="Role within the restaurant hierarchy or research framework"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact telephone number for kitchen alerts / shift coordination"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['user__username']

    def __str__(self):
        full_name = self.user.get_full_name().strip() if self.user else ''
        name_display = full_name if full_name else (self.user.username if self.user else 'Unknown')
        return f'{name_display} ({self.get_role_display()}) - {self.branch}'
