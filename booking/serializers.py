from django.db import transaction
from rest_framework import serializers

from .models import Booking, BookingItem
from .services import available_quantity


class BookingItemSerializer(serializers.ModelSerializer):
    resource_name = serializers.CharField(source='resource.name', read_only=True)

    class Meta:
        model = BookingItem
        fields = ['id', 'resource', 'resource_name', 'quantity']
        read_only_fields = ['id', 'resource_name']


class BookingSerializer(serializers.ModelSerializer):
    items = BookingItemSerializer(many=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'user_name', 'start_date', 'end_date', 'status',
            'items', 'rejection_reason', 'reviewed_by', 'reviewed_by_name',
            'reviewed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'rejection_reason', 'reviewed_by',
            'reviewed_at', 'created_at', 'updated_at'
        ]

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        items = attrs.get('items', [])
        if end_date and start_date and end_date <= start_date:
            raise serializers.ValidationError({'end_date': 'End date must be after start date.'})
        if not items:
            raise serializers.ValidationError({'items': 'Add at least one resource.'})

        resource_ids = [item['resource'].id for item in items]
        if len(resource_ids) != len(set(resource_ids)):
            raise serializers.ValidationError({'items': 'A resource can only appear once in a booking.'})

        for item in items:
            resource = item['resource']
            if not resource.is_active:
                raise serializers.ValidationError({'items': f'{resource.name} is inactive.'})
            available = available_quantity(resource, start_date, end_date)
            if item['quantity'] > available:
                raise serializers.ValidationError({
                    'items': f'Only {available} unit(s) of {resource.name} are available for this period.'
                })
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop('items')
        booking = Booking.objects.create(user=self.context['request'].user, **validated_data)
        BookingItem.objects.bulk_create([BookingItem(booking=booking, **item) for item in items])
        return booking


class RejectBookingSerializer(serializers.Serializer):
    reason = serializers.CharField(min_length=2, max_length=1000)
