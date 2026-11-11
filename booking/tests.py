from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import make_aware
from rest_framework.test import APIClient

from resource.models import Category, Resource
from .models import Booking, BookingItem


class BookingApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.employee = User.objects.create_user(username='employee', email='employee@example.com', password='password123')
        self.manager = User.objects.create_user(
            username='manager', email='manager@example.com', password='password123', role=User.Role.RESOURCE_MANAGER
        )
        category = Category.objects.create(name='Presentation')
        self.projector = Resource.objects.create(name='Projector', category=category, total_quantity=5, location='Store')
        self.client = APIClient()
        self.start = make_aware(datetime(2030, 11, 10, 8, 0))
        self.end = make_aware(datetime(2030, 11, 12, 17, 0))

    def create_booking(self, quantity, start=None, end=None):
        self.client.force_authenticate(self.employee)
        return self.client.post('/api/bookings/', {
            'start_date': start or self.start, 'end_date': end or self.end,
            'items': [{'resource': self.projector.id, 'quantity': quantity}],
        }, format='json')

    def test_employee_can_create_booking(self):
        response = self.create_booking(2)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], Booking.Status.PENDING)

    def test_end_date_must_be_after_start_date(self):
        self.assertEqual(self.create_booking(1, self.end, self.start).status_code, 400)

    def test_manager_can_approve_booking(self):
        booking_id = self.create_booking(2).data['id']
        self.client.force_authenticate(self.manager)
        response = self.client.post(f'/api/bookings/{booking_id}/approve/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], Booking.Status.APPROVED)

    def test_overlapping_bookings_cannot_exceed_quantity(self):
        first_id = self.create_booking(2).data['id']
        self.client.force_authenticate(self.manager)
        self.client.post(f'/api/bookings/{first_id}/approve/')
        second_start = make_aware(datetime(2030, 11, 11, 8, 0))
        second_end = make_aware(datetime(2030, 11, 13, 17, 0))
        second_id = self.create_booking(3, second_start, second_end).data['id']
        self.client.force_authenticate(self.manager)
        self.assertEqual(self.client.post(f'/api/bookings/{second_id}/approve/').status_code, 200)
        self.assertEqual(self.create_booking(4, second_start, self.end).status_code, 400)

    def test_employee_only_sees_own_bookings(self):
        other = get_user_model().objects.create_user(username='other', email='other@example.com', password='password123')
        booking = Booking.objects.create(user=other, start_date=self.start, end_date=self.end)
        BookingItem.objects.create(booking=booking, resource=self.projector, quantity=1)
        self.create_booking(1)
        self.assertEqual(self.client.get('/api/bookings/').data['count'], 1)
