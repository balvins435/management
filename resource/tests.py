from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import make_aware
from rest_framework.test import APIClient

from booking.models import Booking, BookingItem
from .models import Category, Resource


class ResourceApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.employee = User.objects.create_user(username='employee2', email='employee2@example.com', password='password123')
        self.manager = User.objects.create_user(
            username='manager2', email='manager2@example.com', password='password123', role=User.Role.RESOURCE_MANAGER
        )
        self.category = Category.objects.create(name='Computers')
        self.resource = Resource.objects.create(name='Laptop', category=self.category, total_quantity=5, location='Nairobi')
        self.client = APIClient()

    def test_employee_cannot_create_resource(self):
        self.client.force_authenticate(self.employee)
        response = self.client.post('/api/resources/', {
            'name': 'Camera', 'category': self.category.id, 'total_quantity': 2, 'location': 'Nairobi'
        })
        self.assertEqual(response.status_code, 403)

    def test_manager_can_create_resource(self):
        self.client.force_authenticate(self.manager)
        response = self.client.post('/api/resources/', {
            'name': 'Camera', 'category': self.category.id, 'total_quantity': 2, 'location': 'Nairobi'
        })
        self.assertEqual(response.status_code, 201)

    def test_date_range_returns_calculated_availability(self):
        start = make_aware(datetime(2030, 6, 1, 9, 0))
        end = make_aware(datetime(2030, 6, 3, 17, 0))
        booking = Booking.objects.create(user=self.employee, start_date=start, end_date=end, status=Booking.Status.APPROVED)
        BookingItem.objects.create(booking=booking, resource=self.resource, quantity=2)
        self.client.force_authenticate(self.employee)
        response = self.client.get('/api/resources/?start_date=2030-06-02T09:00:00Z&end_date=2030-06-02T17:00:00Z')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['available_quantity'], 3)
