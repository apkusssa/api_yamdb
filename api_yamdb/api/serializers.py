from django.contrib.auth import get_user_model

from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title


User = get_user_model()


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
        slug_field="name",
        read_only=True
    )

    def validate(self, data):
        request = self.context.get("request")
        author = request.user
        title_id = self.context.get("view").kwargs.get("title_id")
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
