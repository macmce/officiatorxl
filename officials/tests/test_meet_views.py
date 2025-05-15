from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from officials.models import Meet, League, Team, Division, Pool, Official, Assignment, Certification, Strategy, Position
from datetime import date, timedelta

User = get_user_model()

class MeetViewsTest(TestCase):
    """Test cases for Meet views."""
    
    def setUp(self):
        """Set up test data."""
        # Create users
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com',
            password='testpassword123'
        )
        
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword123'
        )
        
        # Create leagues
        self.league = League.objects.create(
            name='Test League',
            description='A test league',
            founded_year=2020
        )
        self.league.users.add(self.user)  # Associate with regular user
        
        self.other_league = League.objects.create(
            name='Other League',
            description='Another test league',
            founded_year=2021
        )
        
        # Create divisions
        self.division = Division.objects.create(
            name='Test Division',
            description='A test division',
            league=self.league
        )
        
        self.other_division = Division.objects.create(
            name='Other Division',
            description='Another test division',
            league=self.other_league
        )
        
        # Create teams
        self.team = Team.objects.create(
            name='Test Team',
            abbreviation='TT',
            mascot='Tigers',
            division=self.division
        )
        
        self.team2 = Team.objects.create(
            name='Second Team',
            abbreviation='ST',
            mascot='Sharks',
            division=self.division
        )
        
        self.other_team = Team.objects.create(
            name='Other Team',
            abbreviation='OT',
            mascot='Owls',
            division=self.other_division
        )
        
        # Create pools
        self.pool = Pool.objects.create(
            name='Test Pool',
            address='123 Test Street',
            length=25,
            units='meters',
            lanes=6,
            team=self.team
        )
        
        self.other_pool = Pool.objects.create(
            name='Other Pool',
            address='456 Other Street',
            length=50,
            units='meters',
            lanes=8,
            team=self.other_team
        )
        
        # Create meets
        self.meet = Meet.objects.create(
            name='Test Meet',
            date=date.today() + timedelta(days=7),
            league=self.league,
            host_team=self.team,
            pool=self.pool,
            meet_type='dual'
        )
        self.meet.participating_teams.add(self.team, self.team2)
        
        self.other_meet = Meet.objects.create(
            name='Other Meet',
            date=date.today() + timedelta(days=14),
            league=self.other_league,
            host_team=self.other_team,
            pool=self.other_pool,
            meet_type='invitational'
        )
        self.other_meet.participating_teams.add(self.other_team)
        
        # Create certification for officials
        self.certification = Certification.objects.create(
            name='Test Certification',
            abbreviation='TC',
            description='Test certification',
            level=1
        )
        
        # Create officials
        self.official = Official.objects.create(
            name='Test Official',
            email='official@example.com',
            phone='555-123-4567',
            certification=self.certification,
            team=self.team,
            active=True,
            proficiency='Intermediate'
        )
        
        self.other_official = Official.objects.create(
            name='Other Official',
            email='other@example.com',
            phone='555-987-6543',
            certification=self.certification,
            team=self.other_team,
            active=True,
            proficiency='Advanced'
        )
        
        # Create Strategy
        self.strategy = Strategy.objects.create(name='QUADRANTS')

        # Create position
        self.position = Position.objects.create(
            role='Referee',
            strategy=self.strategy
        )
        
        # Create assignments
        self.assignment = Assignment.objects.create(
            meet=self.meet,
            official=self.official,
            role=self.position.role,  # This now correctly refers to the 'role' field of the Position model
            notes='Head referee'
        )
        
        # Set up the test client
        self.client = Client()
    
    # Meet Tests
    
    def test_meet_list_view_requires_login(self):
        """Test that the meet list view requires login."""
        response = self.client.get(reverse('meet_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('login', response.url)
    
    def test_meet_list_view(self):
        """Test the meet list view shows meets from user's leagues."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Access the meet list page
        response = self.client.get(reverse('meet_list'))
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that only meets from user's leagues are displayed
        self.assertContains(response, 'Test Meet')
        self.assertNotContains(response, 'Other Meet')
        
        # Check context
        self.assertEqual(len(response.context['page_obj']), 1)
        
        # Check that pagination elements are present
        self.assertContains(response, 'Page 1 of 1')
        
        # Check that view toggle is present
        self.assertContains(response, 'id="view-toggle"')
    
    def test_meet_detail_view(self):
        """Test the meet detail view."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Access the meet detail page
        response = self.client.get(reverse('meet_detail', args=[self.meet.id]))
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that meet details are displayed
        self.assertContains(response, 'Test Meet')
        self.assertContains(response, 'Test Pool')
        self.assertContains(response, 'Test Team')
        self.assertContains(response, 'Second Team')  # Participating team
        
        # Check that assignment is shown
        self.assertContains(response, 'Test Official')
        self.assertContains(response, 'Referee')
    
    def test_meet_detail_view_unauthorized(self):
        """Test that users cannot view meets they don't have access to."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Try to access unauthorized meet
        response = self.client.get(reverse('meet_detail', args=[self.other_meet.id]))
        
        # Should redirect with error message
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('meet_list'))
    
    def test_meet_create_view(self):
        """Test creating a meet."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Get the create form
        response = self.client.get(reverse('meet_create'))
        self.assertEqual(response.status_code, 200)
        
        # Check that only leagues and teams from user's access are available
        self.assertContains(response, 'Test League')
        self.assertNotContains(response, 'Other League')
        self.assertContains(response, 'Test Team')
        self.assertNotContains(response, 'Other Team')
        
        # Create a future date for the meet
        future_date = date.today() + timedelta(days=30)
        
        # Post new meet data
        meet_data = {
            'name': 'New Test Meet',
            'date': future_date.strftime('%Y-%m-%d'),
            'league': self.league.id,
            'host_team': self.team.id,
            'pool': self.pool.id,
            'meet_type': 'championship',
            'participating_teams': [self.team.id, self.team2.id]
        }
        
        response = self.client.post(reverse('meet_create'), meet_data)
        
        # Should redirect to detail page of new meet
        self.assertEqual(response.status_code, 302)
        
        # Check that meet was created
        new_meet = Meet.objects.get(name='New Test Meet')
        self.assertEqual(new_meet.meet_type, 'championship')
        self.assertEqual(new_meet.league, self.league)
        self.assertEqual(new_meet.host_team, self.team)
        self.assertEqual(new_meet.participating_teams.count(), 2)
    
    def test_meet_update_view(self):
        """Test updating a meet."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Get the update form
        response = self.client.get(reverse('meet_update', args=[self.meet.id]))
        self.assertEqual(response.status_code, 200)
        
        # Create a future date for the meet
        future_date = date.today() + timedelta(days=21)
        
        # Post updated meet data
        updated_data = {
            'name': 'Updated Meet Name',
            'date': future_date.strftime('%Y-%m-%d'),
            'league': self.league.id,
            'host_team': self.team.id,
            'pool': self.pool.id,
            'meet_type': 'playoff',
            'participating_teams': [self.team.id]  # Changed participating teams
        }
        
        response = self.client.post(reverse('meet_update', args=[self.meet.id]), updated_data)
        
        # Should redirect to detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('meet_detail', args=[self.meet.id]))
        
        # Check that meet was updated
        updated_meet = Meet.objects.get(id=self.meet.id)
        self.assertEqual(updated_meet.name, 'Updated Meet Name')
        self.assertEqual(updated_meet.meet_type, 'playoff')
        self.assertEqual(updated_meet.participating_teams.count(), 1)
    
    def test_meet_update_view_unauthorized(self):
        """Test that users cannot update meets they don't have access to."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Try to update unauthorized meet
        response = self.client.get(reverse('meet_update', args=[self.other_meet.id]))
        
        # Should redirect with error message
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('meet_list'))
    
    def test_meet_delete_view(self):
        """Test deleting a meet."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Get the delete confirmation page
        response = self.client.get(reverse('meet_delete', args=[self.meet.id]))
        self.assertEqual(response.status_code, 200)
        
        # Confirm deletion
        response = self.client.post(reverse('meet_delete', args=[self.meet.id]))
        
        # Should redirect to list page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('meet_list'))
        
        # Check that meet was deleted
        self.assertFalse(Meet.objects.filter(id=self.meet.id).exists())
    
    def test_meet_delete_view_unauthorized(self):
        """Test that users cannot delete meets they don't have access to."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Try to delete unauthorized meet
        response = self.client.get(reverse('meet_delete', args=[self.other_meet.id]))
        
        # Should redirect with error message
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('meet_list'))
        
        # Check that meet still exists
        self.assertTrue(Meet.objects.filter(id=self.other_meet.id).exists())
    
    # Assignment Tests
    
    def test_assignment_list_view_requires_login(self):
        """Test that the assignment list view requires login."""
        response = self.client.get(reverse('assignment_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('login', response.url)
    
    def test_assignment_list_view(self):
        """Test the assignment list view shows assignments from user's leagues."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Access the assignment list page
        response = self.client.get(reverse('assignment_list'))
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that only assignments from user's leagues are displayed
        self.assertContains(response, 'Test Meet')
        self.assertContains(response, 'Test Official')
        self.assertContains(response, 'Referee')
        
        # Check context
        self.assertEqual(len(response.context['page_obj']), 1)
    
    def test_assignment_detail_view(self):
        """Test the assignment detail view."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Access the assignment detail page
        response = self.client.get(reverse('assignment_detail', args=[self.assignment.id]))
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check that assignment details are displayed
        self.assertContains(response, 'Test Meet')
        self.assertContains(response, 'Test Official')
        self.assertContains(response, 'Referee')
        self.assertContains(response, 'Head referee')  # Notes
    
    def test_assignment_detail_view_unauthorized(self):
        """Test that users cannot view assignments they don't have access to."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Create an assignment for other_meet
        other_assignment = Assignment.objects.create(
            meet=self.other_meet,
            official=self.other_official,
            role='Starter'
        )
        
        # Try to access unauthorized assignment
        response = self.client.get(reverse('assignment_detail', args=[other_assignment.id]))
        
        # Should redirect with error message
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('assignment_list'))
    
    def test_assignment_create_view(self):
        """Test creating an assignment."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Get the create form
        response = self.client.get(reverse('assignment_create'))
        self.assertEqual(response.status_code, 200)
        
        # Check that only meets and officials from user's leagues are available
        self.assertContains(response, 'Test Meet')
        self.assertNotContains(response, 'Other Meet')
        self.assertContains(response, 'Test Official')
        self.assertNotContains(response, 'Other Official')
        
        # Post new assignment data
        assignment_data = {
            'meet': self.meet.id,
            'official': self.official.id,
            'role': 'Starter',
            'lane': 1,
            'notes': 'Test notes'
        }
        
        response = self.client.post(reverse('assignment_create'), assignment_data)
        
        # Should redirect to meet detail page
        self.assertEqual(response.status_code, 302)
        
        # Check that assignment was created
        new_assignment = Assignment.objects.get(role='Starter', official=self.official)
        self.assertEqual(new_assignment.meet, self.meet)

        self.assertEqual(new_assignment.notes, 'Test notes')
    
    def test_assignment_create_from_meet(self):
        """Test creating an assignment from a meet page."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Get the create form with meet_id specified
        response = self.client.get(reverse('assignment_create_for_meet', args=[self.meet.id]))
        self.assertEqual(response.status_code, 200)
        
        # The meet should be pre-selected
        self.assertContains(response, f'value="{self.meet.id}" selected')
        
        # Post new assignment data
        assignment_data = {
            'meet': self.meet.id,
            'official': self.official.id,
            'role': 'Stroke Judge',
            'lane': 2,
            'notes': 'From meet page'
        }
        
        response = self.client.post(reverse('assignment_create_for_meet', args=[self.meet.id]), assignment_data)
        
        # Should redirect to meet detail page
        self.assertEqual(response.status_code, 302)
        
        # Check that assignment was created
        new_assignment = Assignment.objects.get(role='Stroke Judge', official=self.official)
        self.assertEqual(new_assignment.meet, self.meet)

    
    def test_assignment_update_view(self):
        """Test updating an assignment."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Get the update form
        response = self.client.get(reverse('assignment_update', args=[self.assignment.id]))
        self.assertEqual(response.status_code, 200)
        
        # Post updated assignment data
        updated_data = {
            'meet': self.meet.id,
            'official': self.official.id,
            'role': 'Chief Judge',  # Changed role
            'lane': 3,
            'notes': 'Updated notes'
        }
        
        response = self.client.post(reverse('assignment_update', args=[self.assignment.id]), updated_data)
        
        # Should redirect to meet detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('meet_detail', args=[self.meet.id]))
        
        # Check that assignment was updated
        updated_assignment = Assignment.objects.get(id=self.assignment.id)
        self.assertEqual(updated_assignment.role, 'Chief Judge')

        self.assertEqual(updated_assignment.notes, 'Updated notes')
    
    def test_assignment_update_view_unauthorized(self):
        """Test that users cannot update assignments they don't have access to."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Create an assignment for other_meet
        other_assignment = Assignment.objects.create(
            meet=self.other_meet,
            official=self.other_official,
            role='Starter'
        )
        
        # Try to update unauthorized assignment
        response = self.client.get(reverse('assignment_update', args=[other_assignment.id]))
        
        # Should redirect with error message
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('assignment_list'))
    
    def test_assignment_delete_view(self):
        """Test deleting an assignment."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Get the delete confirmation page
        response = self.client.get(reverse('assignment_delete', args=[self.assignment.id]))
        self.assertEqual(response.status_code, 200)
        
        # Confirm deletion
        response = self.client.post(reverse('assignment_delete', args=[self.assignment.id]))
        
        # Should redirect to meet detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('meet_detail', args=[self.meet.id]))
        
        # Check that assignment was deleted
        self.assertFalse(Assignment.objects.filter(id=self.assignment.id).exists())
    
    def test_assignment_delete_view_unauthorized(self):
        """Test that users cannot delete assignments they don't have access to."""
        # Login
        self.client.login(username='testuser', password='testpassword123')
        
        # Create an assignment for other_meet
        other_assignment = Assignment.objects.create(
            meet=self.other_meet,
            official=self.other_official,
            role='Starter'
        )
        
        # Try to delete unauthorized assignment
        response = self.client.get(reverse('assignment_delete', args=[other_assignment.id]))
        
        # Should redirect with error message
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('assignment_list'))
        
        # Check that assignment still exists
        self.assertTrue(Assignment.objects.filter(id=other_assignment.id).exists())
