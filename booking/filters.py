import django_filters

from .models import Booking


class BookingFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(field_name='user_id')
    resource = django_filters.NumberFilter(field_name='items__resource_id')
    start_date = django_filters.IsoDateTimeFilter(field_name='start_date', lookup_expr='gte')
    end_date = django_filters.IsoDateTimeFilter(field_name='end_date', lookup_expr='lte')

    class Meta:
        model = Booking
        fields = ['status', 'user', 'resource', 'start_date', 'end_date']
