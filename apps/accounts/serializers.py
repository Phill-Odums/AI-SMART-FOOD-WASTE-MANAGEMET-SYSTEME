from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from apps.organization.models import Branch
from .models import UserProfile

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile including nested Django auth user information.
    """

    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True, default=None)
    chain_name = serializers.CharField(source='branch.chain.name', read_only=True, default=None)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'branch',
            'branch_name',
            'chain_name',
            'role',
            'role_display',
            'phone_number',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        if obj.user:
            return obj.user.get_full_name().strip() or obj.user.username
        return ''


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user along with their associated UserProfile.
    """

    username = serializers.CharField(max_length=150, help_text="Unique login username")
    email = serializers.EmailField(required=False, allow_blank=True, default='', help_text="Email address")
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="User secret password"
    )
    first_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        default='',
        help_text="Given name"
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        default='',
        help_text="Family surname"
    )
    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        required=False,
        allow_null=True,
        default=None,
        help_text="Assigned branch UUID"
    )
    role = serializers.ChoiceField(
        choices=UserProfile.RoleChoices.choices,
        default=UserProfile.RoleChoices.KITCHEN_COOK,
        help_text="Role in the restaurant system"
    )
    phone_number = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        default='',
        help_text="Contact phone number"
    )

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'branch',
            'role',
            'phone_number',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email', '')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        branch = validated_data.pop('branch', None)
        role = validated_data.get('role', UserProfile.RoleChoices.KITCHEN_COOK)
        phone_number = validated_data.get('phone_number', '')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        profile = UserProfile.objects.create(
            user=user,
            branch=branch,
            role=role,
            phone_number=phone_number,
        )
        return profile

    def to_representation(self, instance):
        return UserProfileSerializer(instance, context=self.context).data


class LoginSerializer(serializers.Serializer):
    """
    Serializer for authenticating users and issuing authentication tokens.
    """

    username = serializers.CharField(help_text="Login username")
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Account password"
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.',
                    code='authorization'
                )
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.',
                    code='authorization'
                )
        else:
            raise serializers.ValidationError(
                'Must include "username" and "password".',
                code='authorization'
            )

        attrs['user'] = user
        return attrs
