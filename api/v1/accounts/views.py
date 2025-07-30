from apps.core.models import CustomUser
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    SignupSerializer,
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    TokenRefreshSerializer,
)

User = CustomUser


class AuthViewSet(viewsets.GenericViewSet):
    """
    A viewset that provides authentication endpoints.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=SignupSerializer)
    @action(detail=False, methods=['post'])
    def signup(self, request):
        """
        Register a new user.
        """
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=LoginSerializer)
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Authenticate an existing user and return tokens.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(request_body=ForgotPasswordSerializer)
    @action(detail=False, methods=['post'])
    def forgot_password(self, request):
        """
        Send a password reset link to the user's email.
        """
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Here you would implement the logic to send a password reset email
        return Response({'message': 'Password reset link sent.'})

    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """
        Reset the user's password.
        """
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Here you would implement the logic to reset the password
        return Response({'message': 'Password has been reset.'})

    @swagger_auto_schema(request_body=TokenRefreshSerializer)
    @action(detail=False, methods=['post'])
    def token_refresh(self, request):
        """
        Refresh an access token using a refresh token.
        """
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data['refresh']
        try:
            refresh_token = RefreshToken(refresh)
            return Response({
                'access': str(refresh_token.access_token),
            })
        except Exception as e:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)
