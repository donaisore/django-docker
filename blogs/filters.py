from django_filters import rest_framework as filters

from blogs.fields import CustomDateRangeField
from blogs.models import Blog


class CustomDateRangeFilter(filters.DateFromToRangeFilter):
    field_class = CustomDateRangeField


class BlogFilter(filters.FilterSet):
    # created_at = filters.DateFromToRangeFilter()
    created_at = CustomDateRangeFilter()

    class Meta:
        model = Blog
        fields = ['created_at']
