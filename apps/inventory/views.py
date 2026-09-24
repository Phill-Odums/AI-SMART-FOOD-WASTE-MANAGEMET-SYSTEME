"""Views for the Inventory app.

Provides CRUD endpoints for inventory batches with FEFO sorting, an expiring-soon
alert endpoint for perishable stock, and power outage logs for cold-chain monitoring.
"""

from datetime import timedelta
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import InventoryBatch, PowerOutageLog
from .serializers import (
    InventoryBatchSerializer,
    InventoryBatchListSerializer,
    PowerOutageLogSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary='List inventory batches',
        tags=['Inventory'],
        responses={200: InventoryBatchListSerializer(many=True)}
    ),
    retrieve=extend_schema(
        summary='Retrieve an inventory batch',
        tags=['Inventory'],
        responses={200: InventoryBatchSerializer}
    ),
    create=extend_schema(summary='Create an inventory batch', tags=['Inventory']),
    update=extend_schema(summary='Update an inventory batch', tags=['Inventory']),
    partial_update=extend_schema(summary='Partially update an inventory batch', tags=['Inventory']),
    destroy=extend_schema(summary='Delete an inventory batch', tags=['Inventory']),
)
class InventoryBatchViewSet(viewsets.ModelViewSet):
    """ViewSet for managing ingredient inventory batches with FEFO prioritization."""
    queryset = InventoryBatch.objects.all().select_related('branch', 'ingredient')
    serializer_class = InventoryBatchSerializer
    filterset_fields = ['branch', 'ingredient', 'storage_type', 'is_depleted']
    ordering_fields = ['expiry_date', 'received_date', 'quantity_remaining']
    ordering = ['expiry_date']

    def get_serializer_class(self):
        """Use list serializer for list action and expiring-soon action."""
        if self.action in ['list', 'expiring_soon']:
            return InventoryBatchListSerializer
        return InventoryBatchSerializer

    @extend_schema(
        summary='List batches expiring within 3 days',
        description='Returns non-depleted inventory batches expiring within the next 3 days (expiry_date <= today + 3 days) for kitchen prioritization.',
        tags=['Inventory'],
        responses={200: InventoryBatchListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='expiring-soon')
    def expiring_soon(self, request):
        """Retrieve batches approaching expiry within the next 3 days."""
        today = timezone.now().date()
        cutoff_date = today + timedelta(days=3)
        queryset = self.filter_queryset(
            self.get_queryset().filter(
                expiry_date__lte=cutoff_date,
                is_depleted=False
            )
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary='List power outage logs', tags=['Inventory']),
    retrieve=extend_schema(summary='Retrieve a power outage log', tags=['Inventory']),
    create=extend_schema(summary='Record a power outage log', tags=['Inventory']),
    update=extend_schema(summary='Update a power outage log', tags=['Inventory']),
    partial_update=extend_schema(summary='Partially update a power outage log', tags=['Inventory']),
    destroy=extend_schema(summary='Delete a power outage log', tags=['Inventory']),
)
class PowerOutageLogViewSet(viewsets.ModelViewSet):
    """ViewSet for recording and tracking power grid and generator failures affecting refrigeration."""
    queryset = PowerOutageLog.objects.all().select_related('branch')
    serializer_class = PowerOutageLogSerializer
    filterset_fields = ['branch', 'generator_available']
    ordering_fields = ['outage_start', 'outage_end', 'created_at']
    ordering = ['-outage_start']
