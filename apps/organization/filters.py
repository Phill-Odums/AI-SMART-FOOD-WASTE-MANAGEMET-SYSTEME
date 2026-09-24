import django_filters
from .models import Branch


class BranchFilter(django_filters.FilterSet):
    """FilterSet for Branch model."""

    chain = django_filters.UUIDFilter(field_name='chain__id', lookup_expr='exact')
    city = django_filters.ChoiceFilter(choices=Branch.CityChoices.choices)
    state = django_filters.ChoiceFilter(choices=Branch.StateChoices.choices)
    is_pilot_intervention = django_filters.BooleanFilter()
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Branch
        fields = ['chain', 'city', 'state', 'is_pilot_intervention', 'is_active']
