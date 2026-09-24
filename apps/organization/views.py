from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import RestaurantChain, Branch
from .serializers import (
    RestaurantChainSerializer,
    BranchSerializer,
    BranchListSerializer,
)
from .filters import BranchFilter


@extend_schema_view(
    list=extend_schema(summary="List all restaurant chains", tags=["Organization"]),
    retrieve=extend_schema(summary="Retrieve a restaurant chain", tags=["Organization"]),
    create=extend_schema(summary="Create a new restaurant chain", tags=["Organization"]),
    update=extend_schema(summary="Update a restaurant chain", tags=["Organization"]),
    partial_update=extend_schema(summary="Partially update a restaurant chain", tags=["Organization"]),
    destroy=extend_schema(summary="Delete a restaurant chain", tags=["Organization"]),
)
class RestaurantChainViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Quick Service Restaurant chains.
    """

    queryset = RestaurantChain.objects.all()
    serializer_class = RestaurantChainSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


@extend_schema_view(
    list=extend_schema(
        summary="List all branches",
        description="Retrieve branches with optional filtering by chain, city, state, intervention status, and active status.",
        tags=["Organization"]
    ),
    retrieve=extend_schema(summary="Retrieve a branch", tags=["Organization"]),
    create=extend_schema(summary="Create a new branch", tags=["Organization"]),
    update=extend_schema(summary="Update a branch", tags=["Organization"]),
    partial_update=extend_schema(summary="Partially update a branch", tags=["Organization"]),
    destroy=extend_schema(summary="Delete a branch", tags=["Organization"]),
)
class BranchViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing individual physical restaurant branches.
    """

    queryset = Branch.objects.select_related('chain').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BranchFilter
    search_fields = ['name', 'city']
    ordering_fields = ['name', 'city', 'state', 'created_at']
    ordering = ['chain__name', 'name']

    def get_serializer_class(self):
        """Return BranchListSerializer for list action, otherwise BranchSerializer."""
        if self.action == 'list':
            return BranchListSerializer
        return BranchSerializer
