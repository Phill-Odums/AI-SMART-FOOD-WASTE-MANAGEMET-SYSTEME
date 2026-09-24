from django.contrib import admin
from .models import RestaurantChain, Branch


@admin.register(RestaurantChain)
class RestaurantChainAdmin(admin.ModelAdmin):
    """Admin interface for RestaurantChain model."""

    list_display = ('name', 'headquarters_city', 'branches_count', 'created_at')
    search_fields = ('name', 'headquarters_city')
    ordering = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at')

    @admin.display(description='Total Branches')
    def branches_count(self, obj):
        return obj.branches.count()


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    """Admin interface for Branch model."""

    list_display = (
        'name',
        'chain',
        'city',
        'state',
        'is_pilot_intervention',
        'has_standby_generator',
        'is_active',
        'created_at',
    )
    list_filter = (
        'chain',
        'city',
        'state',
        'is_pilot_intervention',
        'has_standby_generator',
        'is_active',
    )
    search_fields = ('name', 'city', 'chain__name', 'address')
    ordering = ('chain__name', 'name')
    readonly_fields = ('id', 'created_at', 'updated_at')
