from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model."""

    list_display = (
        'username',
        'get_full_name',
        'email',
        'role',
        'branch',
        'phone_number',
        'created_at',
    )
    list_filter = ('role', 'branch__chain', 'branch', 'created_at')
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'phone_number',
        'branch__name',
    )
    ordering = ('user__username',)
    readonly_fields = ('id', 'created_at', 'updated_at')

    @admin.display(description='Username', ordering='user__username')
    def username(self, obj):
        return obj.user.username

    @admin.display(description='Full Name')
    def get_full_name(self, obj):
        return obj.user.get_full_name() or '-'

    @admin.display(description='Email', ordering='user__email')
    def email(self, obj):
        return obj.user.email
