"""URL routing for Waste Tracking application."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DailyWasteSummaryView, WasteLogViewSet

app_name = 'waste'

router = DefaultRouter()
router.register(r'logs', WasteLogViewSet, basename='waste-log')
router.register(r'', WasteLogViewSet, basename='waste')

urlpatterns = [
    path(
        'daily-summary/',
        DailyWasteSummaryView.as_view(),
        name='waste-daily-summary',
    ),
    path('', include(router.urls)),
]
