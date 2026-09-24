"""URL Configuration for the AI Demand Forecasting application."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DailyForecastItemViewSet,
    ForecastRunViewSet,
    KitchenPrepTargetViewSet,
    PrepSheetView,
    TriggerForecastView,
)

app_name = 'forecasting'

router = DefaultRouter()
router.register(r'forecast-runs', ForecastRunViewSet, basename='forecast-run')
router.register(r'forecast-items', DailyForecastItemViewSet, basename='forecast-item')
router.register(r'prep-targets', KitchenPrepTargetViewSet, basename='prep-target')

urlpatterns = [
    path('trigger/', TriggerForecastView.as_view(), name='trigger-forecast'),
    path('prep-sheet/', PrepSheetView.as_view(), name='prep-sheet'),
    path('', include(router.urls)),
]
