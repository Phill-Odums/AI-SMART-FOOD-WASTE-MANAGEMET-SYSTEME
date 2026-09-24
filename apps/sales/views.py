"""Views for Sales Records application.

Provides CRUD endpoints for individual sales records and high-performance
bulk ingestion for Point-of-Sale (POS) batches.
"""

from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers as drf_serializers

from .models import SalesRecord
from .serializers import (
    BulkSalesUploadSerializer,
    SalesRecordListSerializer,
    SalesRecordSerializer,
)


@extend_schema(tags=['Sales Records'])
class SalesRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for managing and querying POS sales transaction records."""

    queryset = SalesRecord.objects.select_related('branch', 'menu_item').all()
    filterset_fields = ['branch', 'menu_item', 'sale_date', 'shift']
    ordering_fields = ['sale_date', 'quantity_sold', 'total_revenue_naira']
    search_fields = ['menu_item__name', 'branch__name']
    ordering = ['-sale_date']

    def get_serializer_class(self):
        """Return optimized list serializer with branch and menu names for list actions."""
        if self.action == 'list':
            return SalesRecordListSerializer
        return SalesRecordSerializer


class BulkSalesUploadView(APIView):
    """Bulk ingestion endpoint for high-volume POS transaction streams."""

    @extend_schema(
        tags=['Sales Records'],
        summary='Bulk ingest POS sales records',
        description=(
            'Ingests a batch of sales records formatted per shift and menu item. '
            'Uses database bulk insertion for optimized performance, returning '
            'the total count of successfully ingested records.'
        ),
        request=BulkSalesUploadSerializer,
        responses={
            201: OpenApiResponse(
                description='Records successfully created',
                response=inline_serializer(
                    name='BulkSalesUploadResponse',
                    fields={
                        'status': drf_serializers.CharField(),
                        'message': drf_serializers.CharField(),
                        'created_count': drf_serializers.IntegerField(),
                    },
                ),
            ),
            400: OpenApiResponse(description='Validation error on incoming payload'),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = BulkSalesUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        records_data = serializer.validated_data['records']
        sales_instances = [
            SalesRecord(
                branch_id=item['branch'],
                menu_item_id=item['menu_item'],
                sale_date=item['sale_date'],
                shift=item['shift'],
                quantity_sold=item['quantity_sold'],
                total_revenue_naira=item['total_revenue_naira'],
            )
            for item in records_data
        ]

        try:
            created_records = SalesRecord.objects.bulk_create(
                sales_instances,
                update_conflicts=True,
                update_fields=['quantity_sold', 'total_revenue_naira', 'updated_at'],
                unique_fields=['branch', 'menu_item', 'sale_date', 'shift'],
            )
        except Exception:
            created_records = SalesRecord.objects.bulk_create(
                sales_instances,
                ignore_conflicts=True,
            )

        count = len(created_records)

        return Response(
            {
                'status': 'success',
                'message': f'Successfully ingested {count} sales records.',
                'created_count': count,
            },
            status=status.HTTP_201_CREATED,
        )
