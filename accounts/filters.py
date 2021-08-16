import django_filters
from django_filters import CharFilter

from .models import *


class OrderFilter(django_filters.FilterSet):
    # Mannually adding filter fields removing(exclude) some filters fields off models
    # start_date = DateFilter(field_name='date_created', lookup_expr='gte')
    # end_date = DateFilter(field_name='date_created', lookup_expr='lte')
    note = CharFilter(field_name='note', lookup_expr='icontains')

    class Meta:
        model = Order
        fields = '__all__'
        exclude = ['date_created']
