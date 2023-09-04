import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)


def category_create(row):
    Category.objects.get_or_create(
        id=row[0],
        name=row[1],
        slug=row[2],
    )


def genre_create(row):
    Genre.objects.get_or_create(
        id=row[0],
        name=row[1],
        slug=row[2],
    )


def titles_create(row):
    Title.objects.get_or_create(
        id=row[0],
        name=row[1],
        year=row[2],
        category_id=row[3],
    )


def genre_title_create(row):
    GenreTitle.objects.get_or_create(
        id=row[0],
        title_id=row[1],
        genre_id=row[2],

    )


def users_create(row):
    User.objects.get_or_create(
        id=row[0],
        username=row[1],
        email=row[2],
        role=row[3],
        first_name=row[4],
        last_name=row[5],
        bio=row[6],
    )


def review_create(row):
    Review.objects.get_or_create(
        id=row[0],
        title_id=row[1],
        text=row[2],
        author_id=row[3],
        score=row[4],
        pub_date=row[5],
    )


def comment_create(row):
    Comment.objects.get_or_create(
        id=row[0],
        review_id=row[1],
        text=row[2],
        author_id=row[3],
        pub_date=row[4],
    )


csv_files = {
    'category.csv': category_create,
    'genre.csv': genre_create,
    'titles.csv': titles_create,
    'genre_title.csv': genre_title_create,
    'users.csv': users_create,
    'review.csv': review_create,
    'comments.csv': comment_create,
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, 'static/data/')
        for key in csv_files.keys():
            with open(path + key, 'r') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    csv_files[key](row)
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
