from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


ROLE_CHOICES = (
        ("user", "пользователь"),
        ("admin", "Администратор"),
        ("moderator", "Модератор")
    )


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        validators=(
            RegexValidator(r"^[\w.@+-]+\Z"),
        ),
        unique=True,
        blank=False
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False
    )
    bio = models.TextField(
        "биография",
        blank=True,
    )
    confirmation_code = models.CharField(
        "Код подтверждения", max_length=36, null=True,
        blank=False, default="XXXX"
    )
    role = models.CharField(
        "Роль",
        max_length=25,
        choices=ROLE_CHOICES,
        blank=True,
        default="user",
        error_messages={"validators": "Вы выбрали несуществующую роль"}
    )

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_moderator(self):
        return self.role == "moderator"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return self.username
