from django.test import TestCase, Client
from django.urls import reverse
from officials.models import Event
from django.contrib.auth import get_user_model

User = get_user_model()

class EventViewsTest(TestCase):
    """Test cases for Event views."""
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com',
            password='testpassword123'
        )
        
        # Create some test events
        Event.objects.create(
            event_number=1,
            name='Freestyle 50m',
            description='Short distance freestyle',
            meet_type='dual',
            gender='male'
        )
        
        Event.objects.create(
            event_number=2,
            name='Butterfly 100m',
            description='Mid distance butterfly',
            meet_type='dual',
            gender='female'
        )
        
        Event.objects.create(
            event_number=1,
            name='Relay 4x100m',
            description='Team relay',
            meet_type='divisional',
            gender='male'
        )
        
        # Set up the test client - use Django's standard Client, not DRF's APIClient
        self.client = Client()
        self.list_url = reverse('event-list')
        
    def test_event_list_view_requires_login(self):
        """Test that the event list view requires login."""
        # Don't login, just make the request with Django's test client
        self.client.logout()
        
        # Make a request to the correct non-API URL with explicit path to avoid API routing
        url = '/officials/events/'
        response = self.client.get(url, HTTP_ACCEPT='text/html', follow=True)
        
        # Print debug information about the response and redirect chain
        print(f"\nResponse status: {response.status_code}")
        print(f"Redirect chain: {response.redirect_chain}")
        
        # Now check that one of the redirects was to the login page (ignoring the status code for now)
        login_redirect = any('login' in redirect_url for redirect_url, status in response.redirect_chain)
        
        # Assertion should pass if we were eventually redirected to login
        self.assertTrue(login_redirect, "Not redirected to login page")
    
    def test_event_list_view(self):
        """Test the event list view displays events."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Access the event list page with direct URL and explicit HTML request
        direct_url = '/officials/events/'
        response = self.client.get(direct_url, HTTP_ACCEPT='text/html')
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that all events are displayed
        self.assertContains(response, 'Freestyle 50m')
        self.assertContains(response, 'Butterfly 100m')
        self.assertContains(response, 'Relay 4x100m')
        
        # Check context
        self.assertTrue(hasattr(response, 'context'), "Response has no context")
        self.assertTrue('events' in response.context, "'events' missing from context")
        self.assertEqual(len(response.context['events']), 3)
    
    def test_event_filter_by_event_number(self):
        """Test filtering events by event number."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Filter by event_number=1 with direct URL and explicit HTML request
        direct_url = '/officials/events/'
        response = self.client.get(direct_url, {'event_number': '1'}, HTTP_ACCEPT='text/html')
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check content directly
        self.assertContains(response, 'Freestyle 50m')
        self.assertContains(response, 'Relay 4x100m')
        # Should not contain Butterfly as it has event_number=2
        self.assertNotContains(response, 'Butterfly 100m')
        self.assertContains(response, 'Relay 4x100m')
        self.assertNotContains(response, 'Butterfly 100m')
    
    def test_event_filter_by_meet_type(self):
        """Test filtering events by meet type."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Filter by meet_type='dual' with direct URL and explicit HTML request
        direct_url = '/officials/events/'
        response = self.client.get(direct_url, {'meet_type': 'dual'}, HTTP_ACCEPT='text/html')
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check content directly
        self.assertContains(response, 'Freestyle 50m')
        self.assertContains(response, 'Butterfly 100m')
        self.assertNotContains(response, 'Relay 4x100m')
    
    def test_event_filter_by_gender(self):
        """Test filtering events by gender."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Filter by gender='male' with direct URL and explicit HTML request
        direct_url = '/officials/events/'
        response = self.client.get(direct_url, {'gender': 'male'}, HTTP_ACCEPT='text/html')
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check content directly
        self.assertContains(response, 'Freestyle 50m')
        self.assertContains(response, 'Relay 4x100m')
        self.assertNotContains(response, 'Butterfly 100m')
    
    def test_event_filter_by_name(self):
        """Test filtering events by name."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Filter by name containing 'Butterfly' with direct URL and explicit HTML request
        direct_url = '/officials/events/'
        response = self.client.get(direct_url, {'name': 'Butterfly'}, HTTP_ACCEPT='text/html')
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check content directly
        self.assertContains(response, 'Butterfly 100m')
        self.assertNotContains(response, 'Freestyle 50m')
        self.assertNotContains(response, 'Relay 4x100m')
    
    def test_event_combined_filters(self):
        """Test using multiple filters together."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Filter by event_number=1 AND gender='male' with direct URL and explicit HTML request
        direct_url = '/officials/events/'
        response = self.client.get(direct_url, {'event_number': '1', 'gender': 'male'}, HTTP_ACCEPT='text/html')
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check content directly
        self.assertContains(response, 'Freestyle 50m')
        self.assertContains(response, 'Relay 4x100m')
        self.assertNotContains(response, 'Butterfly 100m')
        
        # Add more specific filter: event_number=1 AND gender=male AND meet_type=dual with direct URL
        direct_url = '/officials/events/'
        response = self.client.get(direct_url, {'event_number': '1', 'gender': 'male', 'meet_type': 'dual'}, HTTP_ACCEPT='text/html')
        
        # Should have 1 event matching all criteria
        self.assertTrue(hasattr(response, 'context'), "Response has no context")
        self.assertTrue('events' in response.context, "'events' missing from context")
        self.assertEqual(len(response.context['events']), 1)
        self.assertContains(response, 'Freestyle 50m')
        self.assertNotContains(response, 'Relay 4x100m')
        self.assertNotContains(response, 'Butterfly 100m')
    
    def test_delete_selected_events(self):
        """Test deleting selected events."""
        # Login as user with permissions
        self.client.login(username='testuser', password='testpassword123')
        
        # Count initial events
        initial_count = Event.objects.count()
        self.assertEqual(initial_count, 3)
        
        # Get IDs of the events
        event_ids = list(Event.objects.values_list('id', flat=True))
        
        # Delete two events with direct URL and explicit HTML request
        bulk_delete_url = '/officials/events/delete-selected/'  # This is the correct URL from urls.py
        events_list_url = '/officials/events/'
        
        # Debug what we're sending
        print(f"\nEvent IDs: {event_ids}")
        
        # Use the correct parameter name 'selected_events' based on the view implementation
        form_data = {
            'selected_events': [str(event_ids[0]), str(event_ids[1])]
        }
        
        print(f"Form data for delete: {form_data}")
        
        response = self.client.post(bulk_delete_url, form_data, HTTP_ACCEPT='text/html', follow=True)
        
        # Should redirect to event list after successful deletion
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(redirect_url.endswith(events_list_url) for redirect_url, _ in response.redirect_chain))
        
        # Check that we now have one less event
        final_count = Event.objects.count()
        self.assertEqual(final_count, 1)  # Should have deleted 2 out of 3
        
        # Check the right events were deleted
        self.assertEqual(Event.objects.filter(gender='male').count(), 0)
        self.assertEqual(Event.objects.filter(gender='female').count(), 1)
