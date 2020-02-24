from django_filters.fields import DateRangeField

from blogs.widgets import CustomDateRangeWidget


class CustomDateRangeField(DateRangeField):
    widget = CustomDateRangeWidget
