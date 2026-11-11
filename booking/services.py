"""Availability calculations shared by booking and resource endpoints."""

from .models import Booking, BookingItem


def reserved_quantity(resource, start_date, end_date, exclude_booking=None):
    """Return the highest approved quantity reserved during a date range."""
    items = BookingItem.objects.filter(
        resource=resource,
        booking__status=Booking.Status.APPROVED,
        booking__start_date__lt=end_date,
        booking__end_date__gt=start_date,
    ).select_related('booking')
    if exclude_booking:
        items = items.exclude(booking=exclude_booking)

    events = []
    for item in items:
        events.append((max(start_date, item.booking.start_date), 1, item.quantity))
        events.append((min(end_date, item.booking.end_date), 0, -item.quantity))

    current = 0
    highest = 0
    for _, _, amount in sorted(events):
        current += amount
        highest = max(highest, current)
    return highest


def available_quantity(resource, start_date, end_date, exclude_booking=None):
    """Return inventory that remains available throughout a date range."""
    return resource.total_quantity - reserved_quantity(
        resource, start_date, end_date, exclude_booking=exclude_booking
    )


def maximum_reserved_quantity(resource):
    """Return the resource's highest approved reservation at any time."""
    items = BookingItem.objects.filter(
        resource=resource, booking__status=Booking.Status.APPROVED
    ).select_related('booking')
    events = []
    for item in items:
        events.append((item.booking.start_date, 1, item.quantity))
        events.append((item.booking.end_date, 0, -item.quantity))

    current = 0
    highest = 0
    for _, _, amount in sorted(events):
        current += amount
        highest = max(highest, current)
    return highest
