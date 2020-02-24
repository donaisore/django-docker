from django_filters.widgets import DateRangeWidget


class CustomDateRangeWidget(DateRangeWidget):
    suffixes = ['from', 'to']
