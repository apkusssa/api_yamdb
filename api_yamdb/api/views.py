from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.response import Response

from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilterBackend
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleSerializer,
    UserRegistrationSerializer,
)


class UserSignUpViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """Вьюсет для создания обьекта класса User."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user, _ = User.objects.get_or_create(**serializer.validated_data)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject="Код подтверждения",
            message=f"Ваш код подтверждения: {confirmation_code}",
            recipient_list=(user.email,),
            from_email="afonyapav@mail.ru",
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserGetTokenViewSet(mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    """Вьюсет для получения токена."""
    queryset = User.objects.all()
    serializer_class = UserTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            confirmation_code = serializer.validated_data['confirmation_code']
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({'username': 'Пользователь не найден.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if user.confirmation_code == confirmation_code:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key},
                                status=status.HTTP_200_OK)
            else:
                return Response(
                    {'confirmation_code': 'Неправильный код подтверждения.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects.all().annotate(rating=Avg("reviews__score")).order_by("name")
    )
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilterBackend
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return TitleReadSerializer
        return TitleSerializer


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ["get", "post", "patch", "delete"]

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ["get", "post", "patch", "delete"]

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get("review_id"))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
