from rest_framework import serializers

from .models import Category, Resource


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class ResourceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    available_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'total_quantity', 'available_quantity', 'location', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'available_quantity', 'created_at', 'updated_at']

    def get_available_quantity(self, obj) -> int:
        request = self.context.get('request')
        if request and hasattr(request, 'availability_range'):
            from booking.services import available_quantity

            start_date, end_date = request.availability_range
            return available_quantity(obj, start_date, end_date)
        return obj.total_quantity

    def validate_total_quantity(self, value):
        if self.instance:
            from booking.services import maximum_reserved_quantity

            reserved = maximum_reserved_quantity(self.instance)
            if value < reserved:
                raise serializers.ValidationError(
                    f'Total quantity cannot be below the {reserved} unit(s) already reserved.'
                )
        return value
