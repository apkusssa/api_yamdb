from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    ROLE_CHOICES = [
        (USER, 'user'),
        (ADMIN, 'admin'),
        (MODERATOR, 'moderator')
    ]
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField('Имя', max_length=25)
    last_name = models.CharField('Фамилия', max_length=25)
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=256,
        null=True,
        blank=False,
        default='XXXX')
    role = models.CharField(
        'Роль',
        max_length=25,
        choices=ROLE_CHOICES)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField('Категория', max_length=256)
    slug = models.SlugField('Слаг', unique=True, max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField('Жанр', max_length=256)
    slug = models.SlugField('Слаг', unique=True, max_length=50)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.PositiveIntegerField('Год выпуска', max_length=4)
    description = models.TextField('Описание', blank=True)
    genre = models.ManyToManyField(Genre, blank=True, related_name='title')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='title'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name







