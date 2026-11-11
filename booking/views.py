
# API views for creating and managing booking requests

from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from resource.models import Resource
from .filters import BookingFilter
from .models import Booking
from .permissions import BookingPermission
from .serializers import BookingSerializer, RejectBookingSerializer
from .services import available_quantity


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.none()
    serializer_class = BookingSerializer
    permission_classes = [BookingPermission]
    filterset_class = BookingFilter
    ordering_fields = ['start_date', 'end_date', 'created_at', 'status']
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        queryset = Booking.objects.select_related('user', 'reviewed_by').prefetch_related(
            'items__resource'
        ).distinct()
        if getattr(self.request.user, 'role', None) == 'EMPLOYEE':
            queryset = queryset.filter(user=self.request.user)
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        with transaction.atomic():
            booking = Booking.objects.select_for_update().get(pk=self.get_object().pk)
            if booking.status != Booking.Status.PENDING:
                return Response({'detail': 'Only pending bookings can be approved.'}, status=400)

            items = list(booking.items.select_related('resource'))
            resource_ids = sorted(item.resource_id for item in items)
            locked_resources = {
                resource.id: resource
                for resource in Resource.objects.select_for_update().filter(id__in=resource_ids)
            }
            for item in items:
                resource = locked_resources[item.resource_id]
                if not resource.is_active:
                    return Response({'detail': f'{resource.name} is inactive.'}, status=400)
                available = available_quantity(
                    resource, booking.start_date, booking.end_date, exclude_booking=booking
                )
                if item.quantity > available:
                    return Response({
                        'detail': f'Only {available} unit(s) of {resource.name} are available.'
                    }, status=400)

            booking.status = Booking.Status.APPROVED
            booking.reviewed_by = request.user
            booking.reviewed_at = timezone.now()
            booking.rejection_reason = ''
            booking.save(update_fields=[
                'status', 'reviewed_by', 'reviewed_at',
                'rejection_reason', 'updated_at'
            ])
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        booking = self.get_object()
        if booking.status != Booking.Status.PENDING:
            return Response({'detail': 'Only pending bookings can be rejected.'}, status=400)
        serializer = RejectBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking.status = Booking.Status.REJECTED
        booking.rejection_reason = serializer.validated_data['reason']
        booking.reviewed_by = request.user
        booking.reviewed_at = timezone.now()
        booking.save(update_fields=[
            'status', 'rejection_reason', 'reviewed_by',
            'reviewed_at', 'updated_at'
        ])
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status not in [Booking.Status.PENDING, Booking.Status.APPROVED]:
            return Response(
                {'detail': 'Only pending or approved bookings can be cancelled.'},
                status=400
            )
        if booking.end_date <= timezone.now():
            return Response({'detail': 'A booking that has ended cannot be cancelled.'}, status=400)
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        booking = self.get_object()
        if booking.status != Booking.Status.APPROVED:
            return Response({'detail': 'Only approved bookings can be completed.'}, status=400)
        booking.status = Booking.Status.COMPLETED
        booking.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(booking).data)
