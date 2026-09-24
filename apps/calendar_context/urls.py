"""URL routing for Local Calendar Context application."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LocalCalendarContextViewSet, TodayContextView

app_name = 'calendar_context'

router = DefaultRouter()
router.register(r'contexts', LocalCalendarContextViewSet, basename='calendar-context')
router.register(r'', LocalCalendarContextViewSet, basename='calendar')

urlpatterns = [
    path('today/', TodayContextView.as_view(), name='calendar-today'),
    path('', include(router.urls)),
]
