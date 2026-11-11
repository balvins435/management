#Availability calculations shared by booking and resource endpoints.

from .models import Booking, BookingItem

#  Return the highest approved quantity reserved during a date range.
def reserved_quantity(resource, start_date, end_date, exclude_booking=None):
   
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

# Return the available quantity of a resource during a date range.
def available_quantity(resource, start_date, end_date, exclude_booking=None):

    return resource.total_quantity - reserved_quantity(
        resource, start_date, end_date, exclude_booking=exclude_booking
    )

# Return the highest approved quantity reserved at any time for a resource.
def maximum_reserved_quantity(resource):

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
