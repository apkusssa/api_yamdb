from django.contrib import admin

from .models import Category, Genre, User, Title


admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(User)
admin.site.register(Title)
