"""URL routing for the Inventory app."""

from rest_framework.routers import DefaultRouter
from .views import InventoryBatchViewSet, PowerOutageLogViewSet

app_name = 'inventory'

router = DefaultRouter()
router.register(r'batches', InventoryBatchViewSet, basename='inventory-batch')
router.register(r'outages', PowerOutageLogViewSet, basename='power-outage-log')

urlpatterns = router.urls
