"""Views for the Analytics application.

Provides endpoints for menu engineering analysis (Star, Plowhorse, Puzzle, Dog),
generating periodic snapshots from POS sales, waste logs, and Recipe BOMs,
and comparing pre- vs post-intervention KPIs across intervention and control branches.
"""

from decimal import Decimal, ROUND_HALF_UP
import statistics
import uuid

from django.apps import apps
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.menu.models import MenuItem, RecipeBOM
from apps.organization.models import Branch
from .models import MenuEngineeringSnapshot, PilotKPISnapshot
from .serializers import (
    GenerateMenuEngineeringSerializer,
    MenuEngineeringSnapshotSerializer,
    PilotKPISnapshotSerializer,
)


def _get_sales_record_model():
    """Dynamically get the SalesRecord model if apps.sales is installed and loaded."""
    try:
        return apps.get_model('sales', 'SalesRecord')
    except (LookupError, ValueError):
        return None


def _get_waste_log_model():
    """Dynamically get the WasteLog model if apps.waste is installed and loaded."""
    try:
        return apps.get_model('waste', 'WasteLog')
    except (LookupError, ValueError):
        return None


@extend_schema_view(
    list=extend_schema(tags=['Analytics'], summary='List menu engineering matrix snapshots'),
    retrieve=extend_schema(tags=['Analytics'], summary='Retrieve specific menu engineering snapshot'),
)
class MenuEngineeringSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for inspecting periodic menu engineering quadrant classifications."""

    queryset = MenuEngineeringSnapshot.objects.all().select_related('branch', 'menu_item')
    serializer_class = MenuEngineeringSnapshotSerializer
    filterset_fields = ['branch', 'menu_item', 'matrix_category', 'period_start', 'period_end']
    search_fields = ['menu_item__name', 'branch__name', 'recommendation']
    ordering_fields = ['period_end', 'units_sold', 'waste_weight_kg', 'revenue_naira', 'profit_margin_naira']
    ordering = ['-period_end']


@extend_schema_view(
    list=extend_schema(tags=['Analytics'], summary='List pilot quasi-experiment KPI snapshots'),
    retrieve=extend_schema(tags=['Analytics'], summary='Retrieve specific pilot KPI snapshot'),
)
class PilotKPISnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for reviewing pre/post intervention pilot performance indicators."""

    queryset = PilotKPISnapshot.objects.all().select_related('branch')
    serializer_class = PilotKPISnapshotSerializer
    filterset_fields = ['branch', 'period_label', 'snapshot_date']
    search_fields = ['branch__name']
    ordering_fields = [
        'snapshot_date',
        'total_waste_kg',
        'total_waste_cost_naira',
        'total_sales_revenue_naira',
        'waste_to_revenue_ratio',
        'forecast_accuracy_mape',
    ]
    ordering = ['-snapshot_date']


class GenerateMenuEngineeringView(APIView):
    """Triggers dynamic calculation of menu engineering matrix over an observation period."""

    @extend_schema(
        tags=['Analytics'],
        summary='Generate menu engineering matrix (Star, Plowhorse, Puzzle, Dog)',
        description=(
            'Aggregates POS sales records and kitchen waste logs for the specified branch and date range. '
            'Computes raw ingredient costs via Recipe BOM, calculates profit margins, and categorizes '
            'dishes into the 4 menu engineering quadrants based on sales and waste medians.'
        ),
        request=GenerateMenuEngineeringSerializer,
        responses={
            200: MenuEngineeringSnapshotSerializer(many=True),
            400: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        serializer = GenerateMenuEngineeringSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        branch_id = data['branch']
        period_start = data['period_start']
        period_end = data['period_end']

        branch = get_object_or_404(Branch, id=branch_id)

        # Retrieve relevant menu items (associated with the branch chain or active items)
        menu_items = MenuItem.objects.filter(chain=branch.chain, is_active=True)
        if not menu_items.exists():
            menu_items = MenuItem.objects.filter(is_active=True)

        if not menu_items.exists():
            return Response(
                {'detail': 'No active menu items found for branch chain.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 1. Query SalesRecords aggregated by menu_item
        SalesRecord = _get_sales_record_model()
        sales_by_item = {}
        if SalesRecord is not None:
            # Check date field name on SalesRecord (sale_date or date)
            date_field = 'sale_date' if hasattr(SalesRecord, 'sale_date') else 'date'
            sales_filter = {
                'branch': branch,
                f'{date_field}__range': (period_start, period_end),
            }
            sales_qs = (
                SalesRecord.objects.filter(**sales_filter)
                .values('menu_item')
                .annotate(
                    total_sold=Sum('quantity_sold'),
                    total_revenue=Sum('total_revenue_naira'),
                )
            )
            for row in sales_qs:
                sales_by_item[row['menu_item']] = {
                    'units_sold': row['total_sold'] or 0,
                    'revenue_naira': Decimal(str(row['total_revenue'] or '0.00')),
                }

        # 2. Query WasteLogs aggregated by menu_item
        WasteLog = _get_waste_log_model()
        waste_by_item = {}
        if WasteLog is not None:
            waste_qs = (
                WasteLog.objects.filter(
                    branch=branch,
                    menu_item__isnull=False,
                    timestamp__date__range=(period_start, period_end),
                )
                .values('menu_item')
                .annotate(
                    total_kg=Sum('weight_kg'),
                    total_loss=Sum('financial_loss_naira'),
                )
            )
            for row in waste_qs:
                waste_by_item[row['menu_item']] = {
                    'waste_weight_kg': Decimal(str(row['total_kg'] or '0.000')),
                    'waste_cost_naira': Decimal(str(row['total_loss'] or '0.00')),
                }

        # 3. For each menu_item, compute ingredient costs, margins, and assemble dataset
        intermediate_items = []
        for item in menu_items:
            s_data = sales_by_item.get(item.id, {'units_sold': 0, 'revenue_naira': Decimal('0.00')})
            w_data = waste_by_item.get(item.id, {'waste_weight_kg': Decimal('0.000'), 'waste_cost_naira': Decimal('0.00')})

            units_sold = s_data['units_sold']
            revenue_naira = s_data['revenue_naira']
            waste_weight_kg = w_data['waste_weight_kg']
            waste_cost_naira = w_data['waste_cost_naira']

            # Calculate raw ingredient cost via Recipe BOM:
            # sum(quantity_required * ingredient.unit_cost_naira) * units_sold
            boms = RecipeBOM.objects.filter(menu_item=item).select_related('ingredient')
            cost_per_portion = sum(
                (Decimal(str(bom.quantity_required)) * Decimal(str(bom.ingredient.unit_cost_naira)))
                for bom in boms
            )
            ingredient_cost_naira = (cost_per_portion * Decimal(units_sold)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            profit_margin_naira = (revenue_naira - ingredient_cost_naira).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

            intermediate_items.append({
                'menu_item': item,
                'units_sold': units_sold,
                'waste_weight_kg': waste_weight_kg,
                'waste_cost_naira': waste_cost_naira,
                'revenue_naira': revenue_naira,
                'ingredient_cost_naira': ingredient_cost_naira,
                'profit_margin_naira': profit_margin_naira,
            })

        # 4. Compute medians for Sales and Waste across evaluated menu items
        sales_values = [it['units_sold'] for it in intermediate_items]
        waste_values = [float(it['waste_weight_kg']) for it in intermediate_items]

        median_sales = Decimal(str(statistics.median(sales_values))) if sales_values else Decimal('0')
        median_waste = Decimal(str(statistics.median(waste_values))) if waste_values else Decimal('0')

        # 5 & 6. Classify matrix category and assign tailored recommendation
        created_snapshots = []
        with transaction.atomic():
            for it in intermediate_items:
                u_sold = it['units_sold']
                w_kg = it['waste_weight_kg']

                if u_sold >= median_sales and w_kg < median_waste:
                    category = MenuEngineeringSnapshot.MatrixCategory.STAR
                    recommendation = (
                        "Star offering (High Sales, Low Waste): Highly profitable and popular. "
                        "Preserve strict standardized recipe yields, spotlight on digital menu boards, "
                        "and ensure robust ingredient supplier contracts."
                    )
                elif u_sold >= median_sales and w_kg >= median_waste:
                    category = MenuEngineeringSnapshot.MatrixCategory.PLOWHORSE
                    recommendation = (
                        "Plowhorse offering (High Sales, High Waste): Popular with customers but subject to high kitchen loss. "
                        "Enforce staggered batch preparation (65% morning, 35% noon top-up) "
                        "and shorten holding-warmer discard intervals to curb overproduction."
                    )
                elif u_sold < median_sales and w_kg < median_waste:
                    category = MenuEngineeringSnapshot.MatrixCategory.PUZZLE
                    recommendation = (
                        "Puzzle offering (Low Sales, Low Waste): Good operational discipline but underperforming in customer volume. "
                        "Test meal combos, limited-time promotions, or counter staff upselling prompts "
                        "to stimulate demand without escalating food spoilage."
                    )
                else:  # u_sold < median_sales and w_kg >= median_waste
                    category = MenuEngineeringSnapshot.MatrixCategory.DOG
                    recommendation = (
                        "Dog offering (Low Sales, High Waste): Severe drag on kitchen margins. "
                        "Immediate review required: downscale prep batches to on-demand cooking, "
                        "re-engineer ingredients to share stock with Star dishes, or retire from menu."
                    )

                snapshot, _ = MenuEngineeringSnapshot.objects.update_or_create(
                    branch=branch,
                    menu_item=it['menu_item'],
                    period_start=period_start,
                    period_end=period_end,
                    defaults={
                        'units_sold': it['units_sold'],
                        'waste_weight_kg': it['waste_weight_kg'],
                        'waste_cost_naira': it['waste_cost_naira'],
                        'revenue_naira': it['revenue_naira'],
                        'ingredient_cost_naira': it['ingredient_cost_naira'],
                        'profit_margin_naira': it['profit_margin_naira'],
                        'matrix_category': category,
                        'recommendation': recommendation,
                    }
                )
                created_snapshots.append(snapshot)

        out_serializer = MenuEngineeringSnapshotSerializer(created_snapshots, many=True)
        return Response(out_serializer.data, status=status.HTTP_200_OK)


class PilotComparisonView(APIView):
    """Retrieves latest PilotKPISnapshots for all branches and compares Intervention vs Control branches."""

    @extend_schema(
        tags=['Analytics'],
        summary='Quasi-experimental comparison of Intervention vs Control branches',
        description=(
            'Aggregates the latest PilotKPISnapshots across all restaurant branches. '
            'Separates branches into Intervention (AI-assisted) and Control groups, '
            'and calculates comparative waste reduction and financial metrics across '
            'pre-intervention and post-intervention periods.'
        ),
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        snapshots = PilotKPISnapshot.objects.select_related('branch').all()

        # Group latest snapshots per branch and period_label
        branch_periods = {}
        for snap in snapshots:
            key = (snap.branch_id, snap.period_label)
            if key not in branch_periods or snap.snapshot_date > branch_periods[key].snapshot_date:
                branch_periods[key] = snap

        def summarize_group(snaps):
            if not snaps:
                return {
                    'branch_count': 0,
                    'total_waste_kg': Decimal('0.000'),
                    'total_waste_cost_naira': Decimal('0.00'),
                    'total_sales_revenue_naira': Decimal('0.00'),
                    'avg_waste_to_revenue_ratio': Decimal('0.0000'),
                    'avg_forecast_accuracy_mape': None,
                }
            count = len(snaps)
            total_waste_kg = sum((s.total_waste_kg for s in snaps), Decimal('0'))
            total_waste_cost = sum((s.total_waste_cost_naira for s in snaps), Decimal('0'))
            total_revenue = sum((s.total_sales_revenue_naira for s in snaps), Decimal('0'))
            avg_ratio = (sum((s.waste_to_revenue_ratio for s in snaps), Decimal('0')) / Decimal(count)).quantize(
                Decimal('0.0001'), rounding=ROUND_HALF_UP
            )
            mape_vals = [s.forecast_accuracy_mape for s in snaps if s.forecast_accuracy_mape is not None]
            avg_mape = (
                (sum(mape_vals, Decimal('0')) / Decimal(len(mape_vals))).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
                if mape_vals
                else None
            )
            return {
                'branch_count': count,
                'total_waste_kg': total_waste_kg.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP),
                'total_waste_cost_naira': total_waste_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                'total_sales_revenue_naira': total_revenue.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                'avg_waste_to_revenue_ratio': avg_ratio,
                'avg_forecast_accuracy_mape': avg_mape,
            }

        def calculate_impact(pre_summary, post_summary):
            if pre_summary['branch_count'] == 0 or post_summary['branch_count'] == 0:
                return {'status': 'Insufficient data for delta calculation'}

            pre_kg = pre_summary['total_waste_kg']
            post_kg = post_summary['total_waste_kg']
            kg_delta_pct = (
                (((post_kg - pre_kg) / pre_kg) * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if pre_kg > Decimal('0')
                else Decimal('0.00')
            )

            pre_cost = pre_summary['total_waste_cost_naira']
            post_cost = post_summary['total_waste_cost_naira']
            cost_delta_pct = (
                (((post_cost - pre_cost) / pre_cost) * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if pre_cost > Decimal('0')
                else Decimal('0.00')
            )

            pre_ratio = pre_summary['avg_waste_to_revenue_ratio']
            post_ratio = post_summary['avg_waste_to_revenue_ratio']
            ratio_delta_pct = (
                (((post_ratio - pre_ratio) / pre_ratio) * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if pre_ratio > Decimal('0')
                else Decimal('0.00')
            )

            return {
                'waste_weight_delta_pct': kg_delta_pct,
                'waste_cost_delta_pct': cost_delta_pct,
                'waste_to_revenue_ratio_delta_pct': ratio_delta_pct,
            }

        # Partition into intervention vs control
        intervention_pre = [s for s in branch_periods.values() if s.branch.is_pilot_intervention and s.period_label == PilotKPISnapshot.PeriodLabel.PRE_INTERVENTION]
        intervention_post = [s for s in branch_periods.values() if s.branch.is_pilot_intervention and s.period_label == PilotKPISnapshot.PeriodLabel.POST_INTERVENTION]
        control_pre = [s for s in branch_periods.values() if not s.branch.is_pilot_intervention and s.period_label == PilotKPISnapshot.PeriodLabel.PRE_INTERVENTION]
        control_post = [s for s in branch_periods.values() if not s.branch.is_pilot_intervention and s.period_label == PilotKPISnapshot.PeriodLabel.POST_INTERVENTION]

        int_pre_sum = summarize_group(intervention_pre)
        int_post_sum = summarize_group(intervention_post)
        ctrl_pre_sum = summarize_group(control_pre)
        ctrl_post_sum = summarize_group(control_post)

        response_data = {
            'intervention_group': {
                'description': 'Branches deploying the AI Demand Forecasting & Staggered Prep Intervention',
                'pre_intervention': int_pre_sum,
                'post_intervention': int_post_sum,
                'impact_evaluation': calculate_impact(int_pre_sum, int_post_sum),
            },
            'control_group': {
                'description': 'Control branches continuing standard operational practices',
                'pre_intervention': ctrl_pre_sum,
                'post_intervention': ctrl_post_sum,
                'impact_evaluation': calculate_impact(ctrl_pre_sum, ctrl_post_sum),
            },
            'all_snapshots_count': len(branch_periods),
        }

        return Response(response_data, status=status.HTTP_200_OK)
