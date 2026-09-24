"""Views for Local Calendar Context application.

Provides endpoints for inspecting and configuring regional Nigerian calendar variables
and fetching today's contextual parameters on-demand.
"""

from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CityChoices, LocalCalendarContext
from .serializers import (
    LocalCalendarContextSerializer,
    TodayContextSerializer,
)


@extend_schema(tags=['Local Calendar'])
class LocalCalendarContextViewSet(viewsets.ModelViewSet):
    """ViewSet for managing historical and planned regional calendar contexts."""

    queryset = LocalCalendarContext.objects.all()
    serializer_class = LocalCalendarContextSerializer
    filterset_fields = [
        'city',
        'date',
        'traditional_market_day',
        'is_major_market_day',
        'is_payday_window',
        'is_public_holiday',
        'weather_flag',
    ]
    ordering_fields = ['date', 'city', 'created_at']
    ordering = ['-date']


class TodayContextView(APIView):
    """Retrieve or dynamically compute today's local context features for a target city."""

    @extend_schema(
        tags=['Local Calendar'],
        summary="Retrieve today's contextual variables for a city",
        description=(
            "Accepts a 'city' query parameter (e.g. ENUGU, AWKA, OWERRI, ABA, ONITSHA). "
            "Returns today's context. If no record has been created for today, "
            "it is automatically derived and persisted using traditional Igbo calendar algorithms."
        ),
        parameters=[
            OpenApiParameter(
                name='city',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='South-East Nigerian operational city (e.g. ENUGU, AWKA, OWERRI, ONITSHA, ABA)',
            ),
        ],
        responses={200: TodayContextSerializer},
    )
    def get(self, request, *args, **kwargs):
        city_param = request.query_params.get('city')
        if not city_param or not city_param.strip():
            return Response(
                {'error': 'Query parameter "city" is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        city_clean = city_param.strip()
        matched_city = None
        for val, label in CityChoices.choices:
            if city_clean.upper() == val.upper() or city_clean.upper() == label.upper():
                matched_city = val
                break

        if not matched_city:
            matched_city = city_clean.upper()

        today = timezone.localdate()

        context_obj = LocalCalendarContext.objects.filter(
            city=matched_city,
            date=today,
        ).first()

        if not context_obj:
            # Auto-compute and persist context for today
            market_day = LocalCalendarContext.compute_market_day(today)
            is_major = LocalCalendarContext.is_city_major_market(matched_city, market_day)

            context_obj = LocalCalendarContext(
                date=today,
                city=matched_city,
                traditional_market_day=market_day,
                is_major_market_day=is_major,
                weather_flag=LocalCalendarContext.WeatherFlag.SUNNY,
            )
            context_obj.save()

        serializer = TodayContextSerializer(context_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
