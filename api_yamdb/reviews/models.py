from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


User = get_user_model()


class Category(models.Model):
    name = models.CharField("Категория", max_length=256)
    slug = models.SlugField("Слаг", unique=True, max_length=50)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField("Жанр", max_length=256)
    slug = models.SlugField("Слаг", unique=True, max_length=50)

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField("Год выпуска")
    description = models.TextField("Описание", blank=True)
    genre = models.ManyToManyField(Genre, blank=True, related_name="title")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        blank=True, null=True, related_name="title"
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField("Текст")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="reviews", verbose_name="Aвтор"
    )
    score = models.PositiveIntegerField(
        verbose_name="Oценка",
        validators=[
            MinValueValidator(1, message="Оценка должна быть не ниже 1"),
            MaxValueValidator(10, message="Оценка должна быть не выше 10"),
        ],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации", db_index=True
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="произведение",
        null=True,
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ("-pub_date",)
        constraints = (
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_author_title"
            ),
        )

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField("Текст")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="comments", verbose_name="Aвтор"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации", db_index=True
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="oтзыв",
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text[:15]


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        related_name="genretitle",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    title = models.ForeignKey(
        Title,
        related_name="genretitle",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "genre_title"

    def __str__(self):
        return f"{self.genre.name} {self.title.name}"
