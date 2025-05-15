"""
Tests for event management functionality including:
- Creating events
- Viewing events
- Updating events
- Deleting events
- Event model constraints and validation
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.db import transaction
from django.core.exceptions import ValidationError
from officials.models import Event

User = get_user_model()

class EventBaseTest(TestCase):
    """Base test class with common setup for event tests."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.login(username='testuser', password='testpassword')
        
        # Create some test events
        self.event1 = Event.objects.create(
            event_number=1,
            name='Freestyle 50m',
            description='Short distance freestyle',
            meet_type='dual',
            gender='male'
        )
        
        self.event2 = Event.objects.create(
            event_number=2,
            name='Backstroke 100m',
            description='Medium distance backstroke',
            meet_type='dual',
            gender='female'
        )
        
        self.event3 = Event.objects.create(
            event_number=1,
            name='Butterfly 200m',
            description='Long distance butterfly',
            meet_type='divisional',
            gender='male'
        )
        
        # Sample data for new event
        self.new_event_data = {
            'event_number': 5,
            'name': 'Breaststroke 100m',
            'description': 'Medium distance breaststroke',
            'meet_type': 'divisional',
            'gender': 'female'
        }
        
        # URLs
        self.list_url = reverse('event-list')
        self.detail_url = reverse('event-detail', args=[self.event1.pk])
        self.create_url = reverse('event-create')
        self.update_url = reverse('event-update', args=[self.event1.pk])
        self.delete_url = reverse('event-delete', args=[self.event1.pk])


class EventModelTest(EventBaseTest):
    """Test cases for the Event model."""
    
    def test_create_event(self):
        """Test creating a new event with all fields."""
        event_count = Event.objects.count()
        new_event = Event.objects.create(
            event_number=10,
            name='New Test Event',
            description='Test description',
            meet_type='dual',
            gender='male'
        )
        self.assertEqual(Event.objects.count(), event_count + 1)
        self.assertEqual(new_event.name, 'New Test Event')
        self.assertEqual(new_event.description, 'Test description')
    
    def test_create_event_without_description(self):
        """Test creating an event without a description (should be optional)."""
        event_count = Event.objects.count()
        new_event = Event.objects.create(
            event_number=11,
            name='No Description Event',
            meet_type='dual',
            gender='female'
        )
        self.assertEqual(Event.objects.count(), event_count + 1)
        # Django may store empty values as '' rather than None
        self.assertTrue(new_event.description == '' or new_event.description is None)
    
    def test_event_number_validation(self):
        """Test that event_number is validated to be between 1-99."""
        # Test too low
        with self.assertRaises(ValidationError):
            event = Event(
                event_number=0,
                name='Invalid Event',
                meet_type='dual',
                gender='male'
            )
            event.full_clean()
        
        # Test too high
        with self.assertRaises(ValidationError):
            event = Event(
                event_number=100,
                name='Invalid Event',
                meet_type='dual',
                gender='male'
            )
            event.full_clean()
    
    def test_unique_constraint(self):
        """Test the unique constraint on event_number + meet_type."""
        # Create the first event
        Event.objects.create(
            event_number=20,
            name='Unique Test Event',
            meet_type='dual',
            gender='male'
        )
        
        # Try to create a second event with the same event_number and meet_type
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Event.objects.create(
                    event_number=20,
                    name='Duplicate Event',
                    meet_type='dual',
                    gender='male'
                )
        
        # Should be able to create with same number but different meet_type
        Event.objects.create(
            event_number=20,
            name='Different Meet Type Event',
            meet_type='divisional',
            gender='male'
        )
        
        # Should be able to create with different number but same meet_type
        Event.objects.create(
            event_number=21,
            name='Different Number Event',
            meet_type='dual',
            gender='male'
        )
    
    def test_ordering(self):
        """Test that events are ordered by event_number, then meet_type."""
        # Clear existing events to avoid unique constraint violations
        Event.objects.all().delete()
        
        # Create events in non-sequential order
        Event.objects.create(event_number=3, name='Event 3', meet_type='dual', gender='male')
        Event.objects.create(event_number=1, name='Event 1', meet_type='divisional', gender='female')
        Event.objects.create(event_number=1, name='Event 1', meet_type='dual', gender='male')
        Event.objects.create(event_number=2, name='Event 2', meet_type='dual', gender='female')
        
        events = list(Event.objects.all())
        
        # Check ordering - event_number is primary sort key
        self.assertEqual(events[0].event_number, 1)
        self.assertEqual(events[1].event_number, 1)
        self.assertEqual(events[2].event_number, 2)
        self.assertEqual(events[3].event_number, 3)
        
        # For same event_number, meet_type is sorted alphabetically ('divisional' before 'dual')
        self.assertEqual(events[0].meet_type, 'divisional')
        self.assertEqual(events[1].meet_type, 'dual')


class EventViewsTest(EventBaseTest):
    """Test cases for the event views."""
    
    def setUp(self):
        """Setup for event view tests using Django's standard client."""
        super().setUp()
        
        # Use standard Django test client instead of DRF client
        self.client = TestCase.client_class()
        self.client.login(username='testuser', password='testpassword')
        
        # Get URLs for event views
        self.list_url = reverse('event-list')
        self.detail_url = reverse('event-detail', kwargs={'pk': self.event1.pk})
        self.create_url = reverse('event-create')
        self.update_url = reverse('event-update', kwargs={'pk': self.event1.pk})
        self.delete_url = reverse('event-delete', kwargs={'pk': self.event1.pk})
    
    def test_event_list_view(self):
        """Test the event list view."""
        # Force client to request HTML
        response = self.client.get(self.list_url, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 200)
        
        # Verify content without template check
        self.assertContains(response, 'Freestyle 50m')
        self.assertContains(response, 'Backstroke 100m')
        self.assertContains(response, 'Butterfly 200m')
    
    def test_event_detail_view(self):
        """Test the event detail view."""
        # Force client to request HTML
        response = self.client.get(self.detail_url, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 200)
        
        # Verify content without template check
        self.assertContains(response, 'Freestyle 50m')
        self.assertContains(response, 'Short distance freestyle')
    
    def test_event_create_view(self):
        """Test the event create view."""
        # Test GET request
        response = self.client.get(self.create_url, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 200)
        
        # Test POST request with valid data
        event_count = Event.objects.count()
        response = self.client.post(self.create_url, self.new_event_data, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertEqual(Event.objects.count(), event_count + 1)
        
        # Check the created event
        new_event = Event.objects.get(name='Breaststroke 100m')
        self.assertEqual(new_event.event_number, 5)
        self.assertEqual(new_event.meet_type, 'divisional')
        self.assertEqual(new_event.gender, 'female')
    
    def test_event_update_view(self):
        """Test the event update view."""
        # Test GET request
        response = self.client.get(self.update_url, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'officials/event_form.html')
        
        # Test POST request with updated data
        updated_data = {
            'event_number': self.event1.event_number,
            'name': 'Updated Event Name',
            'description': 'Updated description',
            'meet_type': self.event1.meet_type,
            'gender': self.event1.gender
        }
        response = self.client.post(self.update_url, updated_data, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Check the updated event
        self.event1.refresh_from_db()
        self.assertEqual(self.event1.name, 'Updated Event Name')
        self.assertEqual(self.event1.description, 'Updated description')
    
    def test_event_delete_view(self):
        """Test the event delete view."""
        # Test GET request (confirmation page)
        response = self.client.get(self.delete_url, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'officials/event_confirm_delete.html')
        
        # Test POST request (actual deletion)
        event_count = Event.objects.count()
        response = self.client.post(self.delete_url, HTTP_ACCEPT='text/html')
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion
        self.assertEqual(Event.objects.count(), event_count - 1)
        
        # Check that the event is deleted
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(pk=self.event1.pk)
    
    def test_event_delete_selected(self):
        """Test the delete selected events view."""
        event_count = Event.objects.count()
        selected_ids = [self.event1.pk, self.event2.pk]
        
        response = self.client.post(
            reverse('event-delete-selected'),
            {'selected_events': selected_ids},
            HTTP_ACCEPT='text/html'
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion
        self.assertEqual(Event.objects.count(), event_count - 2)
        
        # Check that the selected events are deleted
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(pk=self.event1.pk)
        
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(pk=self.event2.pk)
        
        # Check that non-selected event still exists
        self.assertTrue(Event.objects.filter(pk=self.event3.pk).exists())
