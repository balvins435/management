import django_filters

from .models import Resource


class ResourceFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='category_id')
    location = django_filters.CharFilter(field_name='location', lookup_expr='icontains')
    active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Resource
        fields = ['category', 'location', 'active']
