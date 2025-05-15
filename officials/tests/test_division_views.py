from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from officials.models import League, Division, Team
from officials.forms import DivisionForm

User = get_user_model()

class DivisionViewsTest(TestCase):
    """Test cases for Division views."""

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
        self.league1 = League.objects.create(
            name='League One',
            description='First test league',
            founded_year=2020
        )
        self.league1.users.add(self.user)  # Associate user with league1

        self.league2 = League.objects.create(
            name='League Two',
            description='Second test league',
            founded_year=2021
        )
        # league2 is not associated with self.user initially

        # Create divisions
        self.division1_l1 = Division.objects.create(
            name='Division 1 in League One',
            description='Test division 1 in L1',
            league=self.league1
        )
        self.division2_l1 = Division.objects.create(
            name='Division 2 in League One',
            description='Test division 2 in L1',
            league=self.league1
        )
        self.division1_l2 = Division.objects.create(
            name='Division 1 in League Two',
            description='Test division 1 in L2',
            league=self.league2
        )

        # Create teams for detail view testing
        self.team1_d1_l1 = Team.objects.create(
            name='Team 1 in Div1 L1',
            abbreviation='T1D1L1',
            division=self.division1_l1
        )

        self.client = Client()

    def test_division_list_view_requires_login(self):
        """Test that the division list view requires login."""
        response = self.client.get(reverse('division_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_division_list_view_user_access(self):
        """Test division list view shows divisions from user's leagues."""
        self.client.login(username='testuser', password='testpassword123')

        # Check initial queryset before it goes into the filter and paginator in the view
        user_leagues_test = self.user.leagues.all()
        expected_initial_divisions = Division.objects.filter(league__in=user_leagues_test)
        self.assertIn(self.division1_l1, expected_initial_divisions, "Division1_L1 not in expected initial queryset for user")
        self.assertIn(self.division2_l1, expected_initial_divisions, "Division2_L1 not in expected initial queryset for user")
        self.assertNotIn(self.division1_l2, expected_initial_divisions, "Division1_L2 unexpectedly in initial queryset for user")

        response = self.client.get(reverse('division_list'))
        self.assertEqual(response.status_code, 200)

        # Check the filter object from the context
        division_filter_from_context = response.context.get('filter')
        self.assertIsNotNone(division_filter_from_context, "division_filter not found in response context")
        if division_filter_from_context:
            self.assertIn(self.division1_l1, division_filter_from_context.qs, 
                          f"Division1_L1 not in division_filter.qs. Filtered queryset pks: {[d.pk for d in division_filter_from_context.qs]}")
            self.assertIn(self.division2_l1, division_filter_from_context.qs, 
                          f"Division2_L1 not in division_filter.qs. Filtered queryset pks: {[d.pk for d in division_filter_from_context.qs]}")
        page_obj = response.context.get('page_obj')
        self.assertIsNotNone(page_obj, "page_obj not found in response context")

        if page_obj:
            self.assertTrue(len(page_obj.object_list) >= 2, 
                            f"Expected at least 2 divisions for user, got {len(page_obj.object_list)}. Names: {[d.name for d in page_obj.object_list]}")
            object_list_names = [d.name for d in page_obj.object_list]
            object_list_pks = [d.pk for d in page_obj.object_list]
            error_message_suffix = (f"Found names in page_obj: {object_list_names}. "
                                  f"Found IDs in page_obj: {object_list_pks}.")

            # Check for division1_l1 (expected to be present)
            self.assertIn(self.division1_l1, page_obj.object_list,
                          f"Division1_L1 (Name: '{self.division1_l1.name}', ID: {self.division1_l1.pk}) "
                          f"not in page_obj.object_list. {error_message_suffix}")
            response_content_str = response.content.decode('utf-8')
            expected_name_d1_l1 = self.division1_l1.name
            expected_name_d2_l1 = self.division2_l1.name
            unexpected_name_d1_l2 = self.division1_l2.name

            search_str_d1_l1 = f">{expected_name_d1_l1}<"
            if search_str_d1_l1 not in response_content_str:
                self.fail(f"'{search_str_d1_l1}' (specifically, as tag content) not found in response content (test_division_list_view_user_access, searched full content).\nFull response content:\n{response_content_str}")

            # Check for division2_l1 (expected to be present)
            self.assertIn(self.division2_l1, page_obj.object_list,
                          f"Division2_L1 (Name: '{self.division2_l1.name}', ID: {self.division2_l1.pk}) "
                          f"not in page_obj.object_list. {error_message_suffix}")
            search_str_d2_l1 = f">{expected_name_d2_l1}<"
            if search_str_d2_l1 not in response_content_str:
                self.fail(f"'{search_str_d2_l1}' (specifically, as tag content) not found in response content (test_division_list_view_user_access, searched full content).\nFull response content:\n{response_content_str}")

            # Check for division1_l2 (expected to be absent)
            self.assertNotIn(self.division1_l2, page_obj.object_list,
                             f"Division1_L2 (Name: '{self.division1_l2.name}', ID: {self.division1_l2.pk}) "
                             f"unexpectedly found in page_obj.object_list. {error_message_suffix}")
            search_str_d1_l2 = f">{unexpected_name_d1_l2}<"
            if search_str_d1_l2 in response_content_str:
                self.fail(f"'{search_str_d1_l2}' (specifically, as tag content) unexpectedly found in response content (test_division_list_view_user_access, searched full content).\nFull response content:\n{response_content_str}")
        self.assertIn('page_obj', response.context)
        self.assertIn('filter', response.context)

    def test_division_list_view_admin_access(self):
        """Test division list view for admin shows all divisions."""
        self.client.login(username='adminuser', password='adminpassword123')
        response = self.client.get(reverse('division_list'))
        self.assertEqual(response.status_code, 200)

        page_obj = response.context.get('page_obj')
        self.assertIsNotNone(page_obj, "page_obj not found in admin response context")
        if page_obj:
            admin_object_list = page_obj.object_list
            self.assertIn(self.division1_l1, admin_object_list, "Division1_L1 not in admin's page_obj.object_list")
            self.assertIn(self.division2_l1, admin_object_list, "Division2_L1 not in admin's page_obj.object_list")
            self.assertIn(self.division1_l2, admin_object_list, "Division1_L2 not in admin's page_obj.object_list")

        response_content_str = response.content.decode('utf-8')
        expected_name_d1_l1 = self.division1_l1.name
        expected_name_d2_l1 = self.division2_l1.name
        expected_name_d1_l2 = self.division1_l2.name # For admin, this is expected

        search_str_d1_l1 = f">{expected_name_d1_l1}<"
        if search_str_d1_l1 not in response_content_str:
            self.fail(f"'{search_str_d1_l1}' (specifically, as tag content) not found in admin response content (searched full content).\nFull response content:\n{response_content_str}")

        search_str_d2_l1 = f">{expected_name_d2_l1}<"
        if search_str_d2_l1 not in response_content_str:
            self.fail(f"'{search_str_d2_l1}' (specifically, as tag content) not found in admin response content (searched full content).\nFull response content:\n{response_content_str}")

        search_str_d1_l2 = f">{expected_name_d1_l2}<"
        if search_str_d1_l2 not in response_content_str: # Admin should see this division
            self.fail(f"'{search_str_d1_l2}' (specifically, as tag content) not found in admin response content (should be present, searched full content).\nFull response content:\n{response_content_str}")

        # If all manual checks pass, explicitly pass this part of the test
        self.assertTrue(True, "All manual content string checks passed for admin access list view.")

    def test_division_detail_view_user_access(self):
        """Test division detail view for an accessible division."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('division_detail', args=[self.division1_l1.pk]))
        self.assertEqual(response.status_code, 200)
        response_content_str = response.content.decode('utf-8')
        expected_name_d1_l1 = self.division1_l1.name
        expected_name_team1_d1_l1 = self.team1_d1_l1.name

        if expected_name_d1_l1 not in response_content_str:
            content_snippet = response_content_str[:2000] + ('...' if len(response_content_str) > 2000 else '')
            self.fail(f"'{expected_name_d1_l1}' not found in response content.\nFirst 2000 chars of response content:\n{content_snippet}")

        if expected_name_team1_d1_l1 not in response_content_str:
            content_snippet = response_content_str[:2000] + ('...' if len(response_content_str) > 2000 else '')
            self.fail(f"'{expected_name_team1_d1_l1}' not found in response content.\nFirst 2000 chars of response content:\n{content_snippet}")
        self.assertContains(response, self.division1_l1.name)
        self.assertContains(response, self.team1_d1_l1.name) # Check for associated team

    def test_division_detail_view_user_no_access(self):
        """Test division detail view for a non-accessible division redirects."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('division_detail', args=[self.division1_l2.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('division_list'))

    def test_division_detail_view_admin_access(self):
        """Test division detail view for admin for any division."""
        self.client.login(username='adminuser', password='adminpassword123')
        response = self.client.get(reverse('division_detail', args=[self.division1_l2.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.division1_l2.name)

    def test_division_create_view_get(self):
        """Test GET request for division create view."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('division_create'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], DivisionForm)
        # Check that league choices are limited to user's leagues
        form_league_queryset = response.context['form'].fields['league'].queryset
        self.assertIn(self.league1, form_league_queryset)
        self.assertNotIn(self.league2, form_league_queryset)

    def test_division_create_view_post_success(self):
        """Test POST request for successful division creation."""
        self.client.login(username='testuser', password='testpassword123')
        division_data = {
            'name': 'New Division',
            'description': 'A brand new division.',
            'league': self.league1.pk
        }
        response = self.client.post(reverse('division_create'), division_data)
        self.assertEqual(response.status_code, 302) # Redirects on success
        new_division = Division.objects.get(name='New Division')
        self.assertRedirects(response, reverse('division_detail', args=[new_division.pk]))
        self.assertEqual(new_division.league, self.league1)

    def test_division_create_view_post_no_access_league(self):
        """Test POST to create division in a league user doesn't manage."""
        self.client.login(username='testuser', password='testpassword123')
        division_data = {
            'name': 'Illegal Division',
            'description': 'Should not be created.',
            'league': self.league2.pk # User does not manage league2
        }
        response = self.client.post(reverse('division_create'), division_data)
        # Should show form again with error or redirect with message
        # Current implementation redirects with message
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('division_list'))
        self.assertFalse(Division.objects.filter(name='Illegal Division').exists())

    def test_division_create_view_admin_can_create_in_any_league(self):
        """Test admin can create division in any league."""
        self.client.login(username='adminuser', password='adminpassword123')
        division_data = {
            'name': 'Admin Created Division',
            'description': 'Admin can create this.',
            'league': self.league2.pk
        }
        response = self.client.post(reverse('division_create'), division_data)
        self.assertEqual(response.status_code, 302)
        new_division = Division.objects.get(name='Admin Created Division')
        self.assertRedirects(response, reverse('division_detail', args=[new_division.pk]))
        self.assertEqual(new_division.league, self.league2)

    def test_division_update_view_get(self):
        """Test GET request for division update view."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('division_update', args=[self.division1_l1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], DivisionForm)
        self.assertEqual(response.context['form'].instance, self.division1_l1)
        # Check league queryset for form
        form_league_queryset = response.context['form'].fields['league'].queryset
        self.assertIn(self.league1, form_league_queryset)
        self.assertNotIn(self.league2, form_league_queryset)

    def test_division_update_view_post_success(self):
        """Test POST request for successful division update."""
        self.client.login(username='testuser', password='testpassword123')
        updated_data = {
            'name': 'Updated Division Name',
            'description': self.division1_l1.description,
            'league': self.division1_l1.league.pk
        }
        response = self.client.post(reverse('division_update', args=[self.division1_l1.pk]), updated_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('division_detail', args=[self.division1_l1.pk]))
        self.division1_l1.refresh_from_db()
        self.assertEqual(self.division1_l1.name, 'Updated Division Name')

    def test_division_update_view_post_no_access(self):
        """Test POST to update division user doesn't have access to."""
        self.client.login(username='testuser', password='testpassword123')
        updated_data = {'name': 'Cannot Update This'}
        response = self.client.post(reverse('division_update', args=[self.division1_l2.pk]), updated_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('division_list'))
        self.division1_l2.refresh_from_db()
        self.assertNotEqual(self.division1_l2.name, 'Cannot Update This')

    def test_division_delete_view_get(self):
        """Test GET request for division delete confirmation view."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('division_delete', args=[self.division1_l1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.division1_l1.name)

    def test_division_delete_view_post_success(self):
        """Test POST request for successful division deletion."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.post(reverse('division_delete', args=[self.division1_l1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('division_list'))
        self.assertFalse(Division.objects.filter(pk=self.division1_l1.pk).exists())

    def test_division_delete_view_post_no_access(self):
        """Test POST to delete division user doesn't have access to."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.post(reverse('division_delete', args=[self.division1_l2.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('division_list'))
        self.assertTrue(Division.objects.filter(pk=self.division1_l2.pk).exists())
