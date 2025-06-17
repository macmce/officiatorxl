from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from officials.models import Position, Strategy, Certification
from officials.forms import PositionForm

User = get_user_model()


class PositionViewsTest(TestCase):
    """Test cases for position views."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        # Create certifications
        self.cert_level_2 = Certification.objects.create(
            name='Level 2',
            abbreviation='L2',
            description='Intermediate certification',
            level=2
        )
        
        self.cert_level_3 = Certification.objects.create(
            name='Level 3',
            abbreviation='L3',
            description='Advanced certification',
            level=3
        )
        
        # Create a test strategy
        self.strategy = Strategy.objects.create(
            name='Standard',
            description='Standard strategy'
        )
        
        # Create test positions with and without minimum certification
        self.position_with_cert = Position.objects.create(
            role='Referee',
            strategy=self.strategy,
            location='Pool Deck',
            minimum_certification=self.cert_level_3
        )
        
        self.position_without_cert = Position.objects.create(
            role='Timer',
            strategy=self.strategy,
            location='Lane 1',
            minimum_certification=None
        )
        
        # Set up the test client
        self.client = Client(HTTP_ACCEPT='text/html')
        # Use HTML view URL, not API URL
        self.list_url = reverse('position_list')  # Changed from 'position-list' to 'position_list'
        self.create_url = reverse('position_create')
        self.update_url = reverse('position_update', kwargs={'pk': self.position_with_cert.pk})
        
    def test_position_list_view_requires_login(self):
        """Test that the position list view requires login."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 302)  # Redirects to login page
        
    def test_position_list_view_with_login(self):
        """Test that the position list view works when logged in."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        
        # Check that both positions are in the context
        self.assertIn('page_obj', response.context)
        positions = list(response.context['page_obj'])
        self.assertEqual(len(positions), 2)
        
        # Check HTML content for positions and their minimum certifications
        self.assertContains(response, 'Referee')
        self.assertContains(response, 'Timer')
        self.assertContains(response, 'Pool Deck')
        self.assertContains(response, 'Lane 1')
        
        # Check that the minimum certification is displayed
        self.assertContains(response, 'Level 3')  # For position with certification
        self.assertContains(response, 'None')  # For position without certification
        
    def test_position_create_view_get(self):
        """Test GET request to position create view."""
        self.client.login(username='testuser', password='testpassword123')
        
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        
        # Check that the form in the context has the minimum_certification field
        form = response.context['form']
        self.assertIsInstance(form, PositionForm)
        self.assertIn('minimum_certification', form.fields)
        
        # Check that the form renders the minimum_certification field in HTML
        self.assertContains(response, 'id_minimum_certification')
        
    def test_position_create_view_post_with_certification(self):
        """Test creating a position with a minimum certification."""
        self.client.login(username='testuser', password='testpassword123')
        
        response = self.client.post(self.create_url, {
            'role': 'Stroke Judge',
            'strategy': self.strategy.id,
            'location': 'Side of Pool',
            'minimum_certification': self.cert_level_2.id
        }, follow=True)
        
        # Should redirect to position list after successful creation
        self.assertRedirects(response, self.list_url)
        
        # Check that the position was created with the minimum certification
        new_position = Position.objects.get(role='Stroke Judge')
        self.assertEqual(new_position.minimum_certification, self.cert_level_2)
        
    def test_position_create_view_post_without_certification(self):
        """Test creating a position without a minimum certification."""
        self.client.login(username='testuser', password='testpassword123')
        
        response = self.client.post(self.create_url, {
            'role': 'Announcer',
            'strategy': self.strategy.id,
            'location': 'Admin Area',
            'minimum_certification': ''  # Empty string for no certification
        }, follow=True)
        
        # Should redirect to position list after successful creation
        self.assertRedirects(response, self.list_url)
        
        # Check that the position was created without a minimum certification
        new_position = Position.objects.get(role='Announcer')
        self.assertIsNone(new_position.minimum_certification)
        
    def test_position_update_view(self):
        """Test updating a position's minimum certification."""
        self.client.login(username='testuser', password='testpassword123')
        
        # Change the minimum certification from Level 3 to Level 2
        response = self.client.post(self.update_url, {
            'role': 'Referee',
            'strategy': self.strategy.id,
            'location': 'Pool Deck',
            'minimum_certification': self.cert_level_2.id
        }, follow=True)
        
        # Should redirect to position list after successful update
        self.assertRedirects(response, self.list_url)
        
        # Refresh the position from the database
        self.position_with_cert.refresh_from_db()
        
        # Check that the minimum certification was updated
        self.assertEqual(self.position_with_cert.minimum_certification, self.cert_level_2)
        
    def test_position_update_remove_certification(self):
        """Test removing a position's minimum certification."""
        self.client.login(username='testuser', password='testpassword123')
        
        # Remove the minimum certification
        response = self.client.post(self.update_url, {
            'role': 'Referee',
            'strategy': self.strategy.id,
            'location': 'Pool Deck',
            'minimum_certification': ''  # Empty string to remove certification
        }, follow=True)
        
        # Should redirect to position list after successful update
        self.assertRedirects(response, self.list_url)
        
        # Refresh the position from the database
        self.position_with_cert.refresh_from_db()
        
        # Check that the minimum certification was removed
        self.assertIsNone(self.position_with_cert.minimum_certification)
