from rest_framework import serializers
from apps.core.models import CustomUser

User = CustomUser


class SignupSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Create and return a new user.
        """
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for the forgot password functionality.
    """
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for resetting the user's password.
    """
    password = serializers.CharField()
    password_confirm = serializers.CharField()

    def validate(self, data):
        """
        Validate that the two password fields match.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data


class TokenRefreshSerializer(serializers.Serializer):
    """
    Serializer for refreshing an access token.
    """
    refresh = serializers.CharField()
