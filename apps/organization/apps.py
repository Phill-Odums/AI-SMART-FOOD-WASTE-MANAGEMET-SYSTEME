from django.apps import AppConfig


class OrganizationConfig(AppConfig):
    """Configuration for the Organization application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.organization'
    verbose_name = 'Organization'
