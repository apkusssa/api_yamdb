import re

from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title, User


class UserAdminSerializer(serializers.ModelSerializer):
    """Просто сериализатор Юзера пока не решил куда его применять."""
    username = serializers.RegexField(regex=r'^[\w.@+-]+$',
                                      max_length=150,
                                      required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        read_only_fields = ("role",)



class UserSerializer(serializers.ModelSerializer):
    """Просто сериализатор Юзера пока не решил куда его применять."""

    class Meta:
        model = User
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации новых пользователей."""
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.RegexField(max_length=150,
                                      required=True,
                                      regex=r'^[\w.@+-]+$')

    class Meta:
        model = User
        fields = ("username", "email", "role")

    def validate(self, data):
        if data.get('username') == 'me':
            raise serializers.ValidationError('Использование username '
                                              '"me" запрещено!')
        if (User.objects.filter(username=data.get('username'))
                and User.objects.filter(email=data.get('email'))):
            return data
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError('Пользователь с таким username '
                                              'уже существует.')

        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError('Пользователь с таким email '
                                              'уже существует.')
        return data


class UserTokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT-токена."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


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
    rating = serializers.IntegerField(
        source="reviews__score__avg", read_only=True
    )
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

    def validate(self, data):
        request = self.context.get["request"]
        if not request.method == "POST":
            return data
        author = request.user
        title_id = self.context.get("view").kwargs.get("title_id")
        if Review.objects.filter(author=author, title=title_id).exists():
            raise serializers.ValidationError("Вы уже оставили отзыв")
        return data

    class Meta:
        model = Review
        fields = ("id", "text", "author", "score", "pub_date")


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field="username",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")
