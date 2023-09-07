from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title


User = get_user_model()


class UserAdminSerializer(serializers.ModelSerializer):
    """Сериализатор Юзера."""

    ROLE_CHOICES = (
        ("user", 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    )
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(
        max_length=150, required=True, validators=(
            RegexValidator(r'^[\w.@+-]+\Z'),
        )
    )
    role = serializers.ChoiceField(
        choices=ROLE_CHOICES,
        default="user"
    )

    def validate_username(self, value):
        if value.lower() == "me":
            raise serializers.ValidationError("Нельзя использовать это имя")
        return value

    def validate(self, data):
        if User.objects.filter(email=data.get("email"),
                               username=data.get("username")):
            return data
        elif User.objects.filter(email=data.get("email")):
            raise serializers.ValidationError(
                "Такой email уже используется!"
            )
        elif User.objects.filter(username=data.get("username")):
            raise serializers.ValidationError(
                "Такое имя пользователя уже используется!"
            )
        return data

    class Meta:
        model = User
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")
        lookup_field = 'username'
        extra_kwargs = {
            "username": {"required": True},
            "email": {"required": True},
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации новых пользователей."""
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.RegexField(max_length=150,
                                      required=True,
                                      regex=r'^[\w.@+-]+$')

    def validate(self, data):
        if data.get("username") == "me":
            raise serializers.ValidationError('Использование username '
                                              '"me" запрещено!')
        if (User.objects.filter(username=data.get("username"))
                and User.objects.filter(email=data.get("email"))):
            return data
        if User.objects.filter(username=data.get("username")):
            raise serializers.ValidationError("Пользователь с таким username "
                                              "уже существует.")
        if User.objects.filter(email=data.get("email")):
            raise serializers.ValidationError("Пользователь с таким email "
                                              "уже существует.")
        return data

    class Meta:
        model = User
        fields = ("username", "email")


class UserTokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT-токена."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class UserMeSerializer(serializers.ModelSerializer):
    """Сериализатор юзера для изменеия своих данных."""

    username = serializers.CharField(
        max_length=150, required=True, validators=(
            RegexValidator(r'^[\w.@+-]+\Z'),
        )
    )

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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "slug")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("name", "slug")


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field="slug", many=True, queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = ("id", "name", "year", "description", "genre", "category")


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        fields = ("id", "name", "year", "rating",
                  "description", "genre", "category")
        read_only_fields = fields


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field="username",
        read_only=True,
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        if (request.method == "POST" and Review.objects.filter(
            author=author,
            title_id=title_id
        ).exists()):
            raise serializers.ValidationError("Вы уже оставили отзыв")
        return data

    class Meta:
        model = Review
        fields = ("__all__")


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )
    review = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ("__all__")
