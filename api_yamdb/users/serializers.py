from django.contrib.auth import get_user_model

from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User


class UserRegistrationSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ("username", "email")


class UserAdminSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")
        lookup_field = 'username'


class UserMeSerializer(UserSerializer):
    """Сериализатор юзера для изменеия своих данных."""

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role"
        )

        read_only_fields = ["role"]


class UserTokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT-токена."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()
