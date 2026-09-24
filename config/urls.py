"""
Root URL Configuration for the Smart Food-Waste Reduction Framework.

Swagger UI is available at: /api/docs/
ReDoc is available at:      /api/redoc/
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # DRF Browsable API login/logout (session auth convenience)
    path('api-auth/', include('rest_framework.urls')),

    # OpenAPI Schema & Interactive Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # ── Application API Endpoints (v1) ────────────────────────────────
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/organization/', include('apps.organization.urls')),
    path('api/v1/menu/', include('apps.menu.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/waste/', include('apps.waste.urls')),
    path('api/v1/calendar/', include('apps.calendar_context.urls')),
    path('api/v1/sales/', include('apps.sales.urls')),
    path('api/v1/forecast/', include('apps.forecasting.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
]

