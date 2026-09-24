from rest_framework import serializers
from .models import RestaurantChain, Branch


class RestaurantChainSerializer(serializers.ModelSerializer):
    """Serializer for RestaurantChain model representation and management."""

    branches_count = serializers.IntegerField(source='branches.count', read_only=True)

    class Meta:
        model = RestaurantChain
        fields = [
            'id',
            'name',
            'headquarters_city',
            'branches_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BranchSerializer(serializers.ModelSerializer):
    """Serializer for Branch create, retrieve, update, and delete actions."""

    city_display = serializers.CharField(source='get_city_display', read_only=True)
    state_display = serializers.CharField(source='get_state_display', read_only=True)

    class Meta:
        model = Branch
        fields = [
            'id',
            'chain',
            'name',
            'city',
            'city_display',
            'state',
            'state_display',
            'address',
            'is_pilot_intervention',
            'has_standby_generator',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BranchListSerializer(serializers.ModelSerializer):
    """Listing serializer for Branch with nested chain name for quick display."""

    chain_name = serializers.CharField(source='chain.name', read_only=True)
    city_display = serializers.CharField(source='get_city_display', read_only=True)
    state_display = serializers.CharField(source='get_state_display', read_only=True)

    class Meta:
        model = Branch
        fields = [
            'id',
            'chain',
            'chain_name',
            'name',
            'city',
            'city_display',
            'state',
            'state_display',
            'address',
            'is_pilot_intervention',
            'has_standby_generator',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
