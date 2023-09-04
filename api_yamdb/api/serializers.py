from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    """Просто сериализатор Юзера пока не решил куда его применять."""
    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'bio')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации новых пользователей."""
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, data):
        if data.lower() == 'me':
            raise serializers.ValidationError('Использовать имя "me" запрещено.')
        return data

    def validate_email(self, data):
        if User.objects.filter(email=data).exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует.')
        return data


class UserTokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT-токена."""
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError('Пользователь не найден.')
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError('Неправильный код подтверждения.')
        return data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(source='reviews__score__avg',
                                      read_only=True)
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')
        read_only_fields = fields


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True,
    )

    def validate(self, data):
        request = self.context.get['request']
        if not request.method == 'POST':
            return data
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв'
            )
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
