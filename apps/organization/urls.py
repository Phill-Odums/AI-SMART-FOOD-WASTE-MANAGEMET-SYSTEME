from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantChainViewSet, BranchViewSet

app_name = 'organization'

router = DefaultRouter()
router.register(r'chains', RestaurantChainViewSet, basename='restaurant-chain')
router.register(r'branches', BranchViewSet, basename='branch')

urlpatterns = [
    path('', include(router.urls)),
]
