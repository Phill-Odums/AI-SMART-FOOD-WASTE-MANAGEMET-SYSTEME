"""URL Configuration for the Analytics application."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    GenerateMenuEngineeringView,
    MenuEngineeringSnapshotViewSet,
    PilotComparisonView,
    PilotKPISnapshotViewSet,
)

app_name = 'analytics'

router = DefaultRouter()
router.register(r'menu-engineering', MenuEngineeringSnapshotViewSet, basename='menu-engineering')
router.register(r'pilot-kpis', PilotKPISnapshotViewSet, basename='pilot-kpis')

urlpatterns = [
    path('generate-menu-matrix/', GenerateMenuEngineeringView.as_view(), name='generate-menu-matrix'),
    path('menu-matrix/', GenerateMenuEngineeringView.as_view(), name='menu-matrix'),
    path('pilot-comparison/', PilotComparisonView.as_view(), name='pilot-comparison'),
    path('', include(router.urls)),
]
