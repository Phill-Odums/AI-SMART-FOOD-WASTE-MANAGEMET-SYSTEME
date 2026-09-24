"""Views for the Menu app.

Handles CRUD operations for ingredients, finished menu items, and recipe bills
of materials (BOM).
"""

from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Ingredient, MenuItem, RecipeBOM
from .serializers import (
    IngredientSerializer,
    MenuItemSerializer,
    MenuItemDetailSerializer,
    RecipeBOMSerializer,
    RecipeBOMDetailSerializer,
)


@extend_schema_view(
    list=extend_schema(summary='List ingredients', tags=['Menu & Recipes']),
    retrieve=extend_schema(summary='Retrieve an ingredient', tags=['Menu & Recipes']),
    create=extend_schema(summary='Create an ingredient', tags=['Menu & Recipes']),
    update=extend_schema(summary='Update an ingredient', tags=['Menu & Recipes']),
    partial_update=extend_schema(summary='Partially update an ingredient', tags=['Menu & Recipes']),
    destroy=extend_schema(summary='Delete an ingredient', tags=['Menu & Recipes']),
)
class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet for managing raw ingredients and commodity stocks."""
    queryset = Ingredient.objects.all().select_related('chain')
    serializer_class = IngredientSerializer
    filterset_fields = ['chain', 'unit_of_measure', 'is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'unit_cost_naira', 'created_at']
    ordering = ['name']


@extend_schema_view(
    list=extend_schema(summary='List menu items', tags=['Menu & Recipes']),
    retrieve=extend_schema(
        summary='Retrieve a menu item with nested recipe BOM',
        tags=['Menu & Recipes'],
        responses={200: MenuItemDetailSerializer}
    ),
    create=extend_schema(summary='Create a menu item', tags=['Menu & Recipes']),
    update=extend_schema(summary='Update a menu item', tags=['Menu & Recipes']),
    partial_update=extend_schema(summary='Partially update a menu item', tags=['Menu & Recipes']),
    destroy=extend_schema(summary='Delete a menu item', tags=['Menu & Recipes']),
)
class MenuItemViewSet(viewsets.ModelViewSet):
    """ViewSet for finished culinary menu items sold to customers."""
    queryset = MenuItem.objects.all().select_related('chain').prefetch_related('bom_items__ingredient')
    serializer_class = MenuItemSerializer
    filterset_fields = ['chain', 'category', 'is_perishable_daily', 'is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'selling_price_naira', 'category', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        """Use MenuItemDetailSerializer when retrieving a single item."""
        if self.action == 'retrieve':
            return MenuItemDetailSerializer
        return MenuItemSerializer


@extend_schema_view(
    list=extend_schema(
        summary='List recipe BOM entries',
        tags=['Menu & Recipes'],
        responses={200: RecipeBOMDetailSerializer(many=True)}
    ),
    retrieve=extend_schema(
        summary='Retrieve a recipe BOM entry',
        tags=['Menu & Recipes'],
        responses={200: RecipeBOMDetailSerializer}
    ),
    create=extend_schema(summary='Create a recipe BOM entry', tags=['Menu & Recipes']),
    update=extend_schema(summary='Update a recipe BOM entry', tags=['Menu & Recipes']),
    partial_update=extend_schema(summary='Partially update a recipe BOM entry', tags=['Menu & Recipes']),
    destroy=extend_schema(summary='Delete a recipe BOM entry', tags=['Menu & Recipes']),
)
class RecipeBOMViewSet(viewsets.ModelViewSet):
    """ViewSet for Recipe Bill of Materials linking menu items to ingredients."""
    queryset = RecipeBOM.objects.all().select_related('menu_item', 'ingredient')
    serializer_class = RecipeBOMSerializer
    filterset_fields = ['menu_item', 'ingredient']
    ordering_fields = ['menu_item__name', 'ingredient__name', 'quantity_required']
    ordering = ['menu_item', 'ingredient']

    def get_serializer_class(self):
        """Use RecipeBOMDetailSerializer for list and retrieve actions."""
        if self.action in ['list', 'retrieve']:
            return RecipeBOMDetailSerializer
        return RecipeBOMSerializer
