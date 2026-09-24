"""Views for the AI Demand Forecasting application.

Provides endpoints for managing forecast runs, inspecting predictions and batch strategies,
triggering daily ML ensemble runs with automatic BOM prep calculation, and fetching kitchen prep sheets.
"""

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import uuid

from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.menu.models import MenuItem, RecipeBOM
from apps.organization.models import Branch
from .models import DailyForecastItem, ForecastRun, KitchenPrepTarget
from .serializers import (
    DailyForecastItemSerializer,
    ForecastRunDetailSerializer,
    ForecastRunSerializer,
    KitchenPrepTargetSerializer,
    TriggerForecastSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=['AI Forecasting'], summary='List all forecast execution runs'),
    retrieve=extend_schema(tags=['AI Forecasting'], summary='Retrieve forecast run details with predictions and prep targets'),
    create=extend_schema(tags=['AI Forecasting'], summary='Create a forecast run manually'),
    update=extend_schema(tags=['AI Forecasting'], summary='Update a forecast run'),
    partial_update=extend_schema(tags=['AI Forecasting'], summary='Partially update a forecast run'),
    destroy=extend_schema(tags=['AI Forecasting'], summary='Delete a forecast run'),
)
class ForecastRunViewSet(viewsets.ModelViewSet):
    """Viewset for inspecting and managing AI forecast execution runs."""

    queryset = ForecastRun.objects.all().select_related('branch')
    filterset_fields = ['branch', 'forecast_target_date', 'status']
    search_fields = ['branch__name', 'notes']
    ordering_fields = ['executed_at', 'forecast_target_date']
    ordering = ['-executed_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ForecastRunDetailSerializer
        return ForecastRunSerializer


@extend_schema_view(
    list=extend_schema(tags=['AI Forecasting'], summary='List per-item predictions and batching strategies'),
    retrieve=extend_schema(tags=['AI Forecasting'], summary='Retrieve specific item prediction details'),
)
class DailyForecastItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for examining per-menu-item ensemble predictions."""

    queryset = DailyForecastItem.objects.all().select_related('forecast_run', 'menu_item')
    serializer_class = DailyForecastItemSerializer
    filterset_fields = ['forecast_run', 'menu_item', 'confidence_level', 'recommended_prep_strategy']
    search_fields = ['menu_item__name', 'forecast_run__branch__name']
    ordering_fields = ['ensemble_prediction', 'disagreement_score', 'batch_1_portions']


@extend_schema_view(
    list=extend_schema(tags=['AI Forecasting'], summary='List raw ingredient kitchen prep targets'),
    retrieve=extend_schema(tags=['AI Forecasting'], summary='Retrieve specific prep target item'),
    create=extend_schema(tags=['AI Forecasting'], summary='Create prep target entry'),
    update=extend_schema(tags=['AI Forecasting'], summary='Update prep target, e.g. actual_used_qty'),
    partial_update=extend_schema(tags=['AI Forecasting'], summary='Partially update prep target, e.g. actual_used_qty'),
    destroy=extend_schema(tags=['AI Forecasting'], summary='Delete prep target entry'),
)
class KitchenPrepTargetViewSet(viewsets.ModelViewSet):
    """Viewset for kitchen prep targets translated from BOM recipes."""

    queryset = KitchenPrepTarget.objects.all().select_related('forecast_run', 'ingredient')
    serializer_class = KitchenPrepTargetSerializer
    filterset_fields = ['forecast_run', 'ingredient']
    search_fields = ['ingredient__name', 'forecast_run__branch__name']
    ordering_fields = ['total_raw_qty_to_prep', 'actual_used_qty', 'variance_qty']


class TriggerForecastView(APIView):
    """Accepts model predictions, calculates ensemble & batching, and translates into kitchen prep sheet via Recipe BOM."""

    @extend_schema(
        tags=['AI Forecasting'],
        summary='Trigger daily demand forecast & kitchen prep BOM translation',
        description=(
            'Accepts portion predictions from Amazon Chronos-Bolt and Google TimesFM for a given branch outlet '
            'and target date. Automatically computes blended ensemble predictions, disagreement divergence scores, '
            'and recommended staggered prep batches (65% / 35%). Then translates portion targets into raw ingredient '
            'prep weights via Recipe Bill of Materials (BOM) including prep yield loss shrinkage.'
        ),
        request=TriggerForecastSerializer,
        responses={
            201: ForecastRunDetailSerializer,
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        serializer = TriggerForecastSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        branch_id = data['branch']
        target_date = data['target_date']
        forecast_data = data['forecast_data']
        notes = data.get('notes', '')

        branch = get_object_or_404(Branch, id=branch_id)

        with transaction.atomic():
            # Update existing or create new forecast run for branch + target date
            forecast_run, _ = ForecastRun.objects.update_or_create(
                branch=branch,
                forecast_target_date=target_date,
                defaults={
                    'status': ForecastRun.Status.SUCCESS,
                    'notes': notes,
                }
            )

            # Clear any previously computed items and prep targets for clean recalculation
            forecast_run.forecast_items.all().delete()
            forecast_run.prep_targets.all().delete()

            # Create DailyForecastItem records (save() auto-computes ensemble, confidence, and batches)
            created_items = []
            for item_data in forecast_data:
                menu_item = get_object_or_404(MenuItem, id=item_data['menu_item'])
                forecast_item = DailyForecastItem(
                    forecast_run=forecast_run,
                    menu_item=menu_item,
                    chronos_prediction=item_data['chronos_prediction'],
                    timesfm_prediction=item_data['timesfm_prediction'],
                )
                forecast_item.save()
                created_items.append(forecast_item)

            # Compute KitchenPrepTarget entries via RecipeBOM
            # Formula: ensemble_prediction * quantity_required * (1 + prep_yield_loss_pct / 100)
            ingredient_totals = {}
            for item in created_items:
                boms = RecipeBOM.objects.filter(menu_item=item.menu_item).select_related('ingredient')
                for bom in boms:
                    loss_multiplier = Decimal('1') + (Decimal(str(bom.prep_yield_loss_pct)) / Decimal('100'))
                    raw_qty = (
                        Decimal(str(item.ensemble_prediction))
                        * Decimal(str(bom.quantity_required))
                        * loss_multiplier
                    )
                    ingredient = bom.ingredient
                    ingredient_totals[ingredient] = ingredient_totals.get(ingredient, Decimal('0')) + raw_qty

            for ingredient, total_qty in ingredient_totals.items():
                KitchenPrepTarget.objects.create(
                    forecast_run=forecast_run,
                    ingredient=ingredient,
                    total_raw_qty_to_prep=total_qty.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
                )

        output_serializer = ForecastRunDetailSerializer(forecast_run)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class PrepSheetView(APIView):
    """Fetches the digital kitchen prep sheet for a branch outlet on a specific date."""

    @extend_schema(
        tags=['AI Forecasting'],
        summary='Retrieve digital kitchen prep sheet for shift opening',
        description=(
            'Returns raw ingredient preparation targets for a branch kitchen. '
            'Query parameters: branch (required UUID), date (optional YYYY-MM-DD, defaults to tomorrow).'
        ),
        parameters=[
            OpenApiParameter(
                name='branch',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                required=True,
                description='UUID of the branch outlet'
            ),
            OpenApiParameter(
                name='date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Target date for prep sheet (YYYY-MM-DD). Defaults to tomorrow.'
            ),
        ],
        responses={
            200: KitchenPrepTargetSerializer(many=True),
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def get(self, request):
        branch_id = request.query_params.get('branch')
        if not branch_id:
            return Response(
                {'detail': 'Query parameter "branch" (UUID) is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        date_str = request.query_params.get('date')
        if date_str:
            try:
                target_date = date.fromisoformat(date_str)
            except ValueError:
                return Response(
                    {'detail': 'Invalid date format. Expected YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            target_date = date.today() + timedelta(days=1)

        forecast_run = (
            ForecastRun.objects.filter(branch_id=branch_id, forecast_target_date=target_date)
            .order_by('-executed_at')
            .first()
        )

        if not forecast_run:
            return Response(
                {'detail': f'No forecast run found for branch {branch_id} on {target_date}.'},
                status=status.HTTP_404_NOT_FOUND
            )

        targets = forecast_run.prep_targets.all().select_related('ingredient')
        serializer = KitchenPrepTargetSerializer(targets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
