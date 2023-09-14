import uuid

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework.pagination import (PageNumberPagination)
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import EMAIL_NAME
from api.permissions import (
    IsAdminOrSuperuser
)
from users.serializers import (
    UserAdminSerializer,
    UserRegistrationSerializer,
    UserMeSerializer,
    UserTokenSerializer
)


User = get_user_model()

methods = ["get", "post", "patch", "delete"]


class UserSignUpViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Вьюсет для создания объекта класса User."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def send_confirmation_code(self, user):
        confirmation_code = str(uuid.uuid4())
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            subject="Код подтверждения",
            message=f"Ваш код подтверждения: {confirmation_code}",
            recipient_list=(user.email,),
            from_email=EMAIL_NAME,
            fail_silently=True
        )

    def create(self, request):
        username = request.data.get("username")
        if username == "me":
            return Response(
                {"username": "Использование 'me' запрещено."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(
                username=username,
                email=request.data.get("email")
            )
            self.send_confirmation_code(user)
            return Response(
                {"detail": "Новый код подтверждения был отправлен."},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                self.send_confirmation_code(user)
                return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def get_jwt_token(request):
    serializer = UserTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    confirmation_code = serializer.validated_data.get("confirmation_code")
    user = get_object_or_404(
        User,
        username=serializer.validated_data["username"]
    )
    if confirmation_code == user.confirmation_code:
        token = AccessToken.for_user(user)
        return Response({"token": str(token)}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = (IsAdminOrSuperuser,)
    lookup_field = "username"
    http_method_names = methods + ["head", "options", "trace"]
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ("username",)
    search_fields = ("username", )
    ordering_fields = ("username",)

    @action(
        methods=["get", "patch"],
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=UserMeSerializer,
        url_path="me")
    def get_user_info(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == "PATCH":
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
