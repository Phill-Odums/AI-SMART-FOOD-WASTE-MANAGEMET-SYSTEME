"""Views for Waste Tracking application.

Provides CRUD endpoints for waste log entries and aggregated daily summary metrics.
"""

from datetime import datetime
from decimal import Decimal
import uuid

from django.db.models import Count, Sum
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WasteLog
from .serializers import (
    WasteDailySummarySerializer,
    WasteLogListSerializer,
    WasteLogSerializer,
)


@extend_schema(tags=['Waste Tracking'])
class WasteLogViewSet(viewsets.ModelViewSet):
    """ViewSet for logging and auditing food waste events."""

    queryset = WasteLog.objects.select_related(
        'branch', 'logged_by__user', 'menu_item', 'ingredient'
    ).all()
    filterset_fields = [
        'branch',
        'operational_stage',
        'root_cause_determinant',
        'menu_item',
        'ingredient',
    ]
    ordering_fields = ['timestamp', 'weight_kg', 'financial_loss_naira']
    search_fields = ['notes']
    ordering = ['-timestamp']

    def get_serializer_class(self):
        """Return optimized list serializer or standard full serializer."""
        if self.action == 'list':
            return WasteLogListSerializer
        return WasteLogSerializer


class DailyWasteSummaryView(APIView):
    """Aggregate daily waste metrics for a specific restaurant branch."""

    @extend_schema(
        tags=['Waste Tracking'],
        summary='Get daily waste summary for a branch',
        description=(
            'Aggregates food waste weight, estimated financial loss in Naira, '
            'and stage breakdown for a branch on a given date (defaults to today).'
        ),
        parameters=[
            OpenApiParameter(
                name='branch',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='UUID of the branch outlet',
            ),
            OpenApiParameter(
                name='date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Target date in YYYY-MM-DD format (defaults to current date)',
            ),
        ],
        responses={200: WasteDailySummarySerializer},
    )
    def get(self, request, *args, **kwargs):
        branch_id = request.query_params.get('branch')
        if not branch_id:
            return Response(
                {'error': 'Query parameter "branch" is required (UUID).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            uuid.UUID(str(branch_id))
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid branch UUID provided.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        date_str = request.query_params.get('date')
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Expected YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            target_date = timezone.localdate()

        logs = WasteLog.objects.filter(
            branch_id=branch_id,
            timestamp__date=target_date,
        )

        aggregates = logs.aggregate(
            total_weight=Sum('weight_kg'),
            total_loss=Sum('financial_loss_naira'),
        )
        total_weight = aggregates['total_weight'] or Decimal('0.000')
        total_loss = aggregates['total_loss'] or Decimal('0.00')
        total_count = logs.count()

        # Breakdown by operational stage
        breakdown_by_stage = {
            stage[0]: {
                'label': str(stage[1]),
                'weight_kg': Decimal('0.000'),
                'loss_naira': Decimal('0.00'),
                'count': 0,
            }
            for stage in WasteLog.OperationalStage.choices
        }

        stage_aggs = logs.values('operational_stage').annotate(
            weight=Sum('weight_kg'),
            loss=Sum('financial_loss_naira'),
            count=Count('id'),
        )

        for agg in stage_aggs:
            stg = agg['operational_stage']
            if stg in breakdown_by_stage:
                breakdown_by_stage[stg]['weight_kg'] = agg['weight'] or Decimal('0.000')
                breakdown_by_stage[stg]['loss_naira'] = agg['loss'] or Decimal('0.00')
                breakdown_by_stage[stg]['count'] = agg['count']

        summary_data = {
            'date': target_date,
            'total_weight_kg': total_weight,
            'total_loss_naira': total_loss,
            'count': total_count,
            'breakdown_by_stage': breakdown_by_stage,
        }

        serializer = WasteDailySummarySerializer(summary_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
