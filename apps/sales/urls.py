"""URL routing for Sales Records application."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BulkSalesUploadView, SalesRecordViewSet

app_name = 'sales'

router = DefaultRouter()
router.register(r'records', SalesRecordViewSet, basename='sales-record')
router.register(r'', SalesRecordViewSet, basename='sales')

urlpatterns = [
    path('bulk-upload/', BulkSalesUploadView.as_view(), name='sales-bulk-upload'),
    path('', include(router.urls)),
]
