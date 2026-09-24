from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers

from .models import UserProfile
from .serializers import (
    UserProfileSerializer,
    RegisterSerializer,
    LoginSerializer,
)


@extend_schema_view(
    list=extend_schema(summary="List all user profiles", tags=["Auth & Accounts"]),
    retrieve=extend_schema(summary="Retrieve user profile by ID", tags=["Auth & Accounts"]),
    create=extend_schema(summary="Create a user profile", tags=["Auth & Accounts"]),
    update=extend_schema(summary="Update a user profile", tags=["Auth & Accounts"]),
    partial_update=extend_schema(summary="Partially update a user profile", tags=["Auth & Accounts"]),
    destroy=extend_schema(summary="Delete a user profile", tags=["Auth & Accounts"]),
)
class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and managing staff user profiles.
    """

    queryset = UserProfile.objects.select_related('user', 'branch', 'branch__chain').all()
    serializer_class = UserProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['branch', 'role']
    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'phone_number',
    ]
    ordering_fields = ['user__username', 'role', 'created_at']
    ordering = ['user__username']


@extend_schema(
    tags=['Auth & Accounts'],
    summary='Register new user and profile',
    description='Create a new authentication user along with an associated role-based UserProfile and branch assignment.',
    request=RegisterSerializer,
    responses={status.HTTP_201_CREATED: UserProfileSerializer}
)
class RegisterView(CreateAPIView):
    """
    Public registration endpoint to onboard staff, managers, and research auditors.
    """

    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


@extend_schema(
    tags=['Auth & Accounts'],
    summary='Log in and obtain auth token',
    description='Authenticate credentials (username/password) and receive a persistent DRF authentication token.',
    request=LoginSerializer,
    responses={
        status.HTTP_200_OK: inline_serializer(
            name='AuthTokenResponse',
            fields={
                'token': serializers.CharField(help_text='DRF authentication token'),
                'user_id': serializers.IntegerField(help_text='Django user ID'),
                'username': serializers.CharField(),
                'email': serializers.EmailField(),
                'profile': UserProfileSerializer(),
            }
        )
    }
)
class LoginView(APIView):
    """
    Authenticate user and return their authentication token and profile.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)

        profile = getattr(user, 'profile', None)
        profile_data = (
            UserProfileSerializer(profile, context={'request': request}).data
            if profile
            else None
        )

        return Response(
            {
                'token': token.key,
                'user_id': user.pk,
                'username': user.username,
                'email': user.email,
                'profile': profile_data,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=['Auth & Accounts'],
    summary='Retrieve current authenticated user profile',
    description='Get profile details, branch assignment, and operational role of the currently logged-in user.',
    responses={status.HTTP_200_OK: UserProfileSerializer}
)
class CurrentUserView(RetrieveAPIView):
    """
    Retrieve the UserProfile belonging to the authenticated user making the request.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        user = self.request.user
        role = (
            UserProfile.RoleChoices.ADMIN
            if (user.is_superuser or user.is_staff)
            else UserProfile.RoleChoices.KITCHEN_COOK
        )
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': role}
        )
        return profile
