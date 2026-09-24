"""URL routing for the Menu app."""

from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, MenuItemViewSet, RecipeBOMViewSet

app_name = 'menu'

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'items', MenuItemViewSet, basename='menu-item')
router.register(r'bom', RecipeBOMViewSet, basename='recipe-bom')

urlpatterns = router.urls
