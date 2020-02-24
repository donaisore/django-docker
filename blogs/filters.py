from django_filters import rest_framework as filters

from blogs.models import Blog


class BlogFilter(filters.FilterSet):
    created_at = filters.DateFromToRangeFilter()

    class Meta:
        model = Blog
        fields = ['created_at']
