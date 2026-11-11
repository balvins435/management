from django.utils.dateparse import parse_datetime
from rest_framework import serializers, viewsets

from booking.services import available_quantity
from .filters import ResourceFilter
from .models import Category, Resource
from .permissions import ResourcePermission
from .serializers import CategorySerializer, ResourceSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ResourcePermission]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class ResourceViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceSerializer
    permission_classes = [ResourcePermission]
    filterset_class = ResourceFilter
    search_fields = ['name', 'description', 'location', 'category__name']
    ordering_fields = ['name', 'total_quantity', 'created_at']

    def get_queryset(self):
        queryset = Resource.objects.select_related('category')
        start_text = self.request.query_params.get('start_date')
        end_text = self.request.query_params.get('end_date')

        if not start_text and not end_text:
            return queryset
        if not start_text or not end_text:
            raise serializers.ValidationError('Both start_date and end_date are required.')

        start_date = parse_datetime(start_text)
        end_date = parse_datetime(end_text)
        if not start_date or not end_date:
            raise serializers.ValidationError('Dates must be valid ISO 8601 date-times.')
        if end_date <= start_date:
            raise serializers.ValidationError('end_date must be after start_date.')

        self.request.availability_range = (start_date, end_date)

        minimum = self.request.query_params.get('available_quantity')
        if minimum:
            try:
                minimum = int(minimum)
            except ValueError:
                raise serializers.ValidationError('available_quantity must be a whole number.')
            matching_ids = [
                resource.id for resource in queryset.filter(is_active=True)
                if available_quantity(resource, start_date, end_date) >= minimum
            ]
            queryset = queryset.filter(id__in=matching_ids)
        return queryset
