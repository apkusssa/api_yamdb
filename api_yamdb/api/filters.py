from django_filters import CharFilter, FilterSet

from reviews.models import Title


class TitleFilterBackend(FilterSet):
    genre = CharFilter(field_name="genre__slug", lookup_expr="icontains")
    category = CharFilter(field_name="category__slug", lookup_expr="icontains")
    name = CharFilter(field_name="name", lookup_expr="contains")

    class Meta:
        model = Title
        fields = ("genre", "category", "name", "year")
