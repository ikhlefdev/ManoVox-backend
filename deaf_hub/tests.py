from rest_framework.test import APITestCase
from django.urls import reverse
from accounts.models import User
from .models import Event
from django.utils import timezone

class EventAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin_test', email='admin@test.com', password='testpass', role='admin'
        )
        self.regular_user = User.objects.create_user(
            username='reg_test', email='reg@test.com', password='testpass', role='user'
        )
        self.url = reverse('event-list')

    def test_admin_can_create_event(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'Deaf Hub Meetup',
            'description': 'A community meetup.',
            'date': timezone.now().isoformat(),
            'location': 'Community Center'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Event.objects.count(), 1)

    def test_regular_user_cannot_create_event(self):
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'title': 'Invalid Event',
            'description': 'Should not be allowed.',
            'date': timezone.now().isoformat(),
            'location': 'Secret Center'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Event.objects.count(), 0)

    def test_anyone_can_list_events(self):
        Event.objects.create(
            title='Test Event', description='desc', date=timezone.now(),
            location='loc', author=self.admin_user
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # response.data could be a dict with 'results' if pagination is active, let's just check length of it or status
        # Since no pagination is specified, response.data should be a list
        self.assertEqual(len(response.data), 1)
