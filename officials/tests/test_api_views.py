from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from officials.models import League, Certification, Division, Team, Official, Meet, Pool, Position, Assignment, Event, Strategy, UserLeagueAdmin
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class LeagueAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        self.league1 = League.objects.create(name='Test League Alpha', founded_year=2020)
        self.league2 = League.objects.create(name='Test League Beta', founded_year=2021)

        # URLS
        self.league_list_url = reverse('league-list') # DefaultRouter generates names like 'modelname-list'
        self.league_detail_url = reverse('league-detail', kwargs={'pk': self.league1.pk})

    def test_list_leagues_unauthenticated(self):
        """Ensure unauthenticated users cannot list leagues."""
        response = self.client.get(self.league_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_retrieve_league_unauthenticated(self):
        """Ensure unauthenticated users cannot retrieve a league."""
        response = self.client.get(self.league_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_leagues_authenticated(self):
        """Ensure authenticated users can list leagues."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(self.league_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # Assuming pagination is not aggressive or default
        self.assertEqual(response.data[0]['name'], self.league1.name)

    def test_retrieve_league_authenticated(self):
        """Ensure authenticated users can retrieve a league."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(self.league_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.league1.name)

    def test_create_league_authenticated(self):
        """Ensure authenticated users can create a league."""
        self.client.login(username='testuser', password='testpassword123')
        data = {'name': 'New Test League', 'founded_year': 2023, 'description': 'A brand new league.'}
        response = self.client.post(self.league_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(League.objects.count(), 3)
        self.assertEqual(League.objects.latest('id').name, 'New Test League')

    def test_create_league_missing_name_authenticated(self):
        """Ensure creating a league with missing required fields fails."""
        self.client.login(username='testuser', password='testpassword123')
        data = {'founded_year': 2023} # Name is required
        response = self.client.post(self.league_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_update_league_authenticated(self):
        """Ensure authenticated users can update a league."""
        self.client.login(username='testuser', password='testpassword123')
        updated_data = {'name': 'Updated Test League Alpha', 'founded_year': 2020, 'description': 'Updated description.'}
        response = self.client.put(self.league_detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.league1.refresh_from_db()
        self.assertEqual(self.league1.name, 'Updated Test League Alpha')
        self.assertEqual(self.league1.description, 'Updated description.')

    def test_partial_update_league_authenticated(self):
        """Ensure authenticated users can partially update a league (PATCH)."""
        self.client.login(username='testuser', password='testpassword123')
        patch_data = {'description': 'Patched description.'}
        response = self.client.patch(self.league_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.league1.refresh_from_db()
        self.assertEqual(self.league1.description, 'Patched description.')
        self.assertEqual(self.league1.name, 'Test League Alpha') # Name should be unchanged

    def test_delete_league_authenticated(self):
        """Ensure authenticated users can delete a league."""
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.delete(self.league_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(League.objects.count(), 1)
        with self.assertRaises(League.DoesNotExist):
            League.objects.get(pk=self.league1.pk)

# We will add more test classes for other ViewSets here later.


class CertificationAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_cert', password='testpassword123')
        self.cert1 = Certification.objects.create(name='Basic Scorer', abbreviation='BS', level=1)
        self.cert2 = Certification.objects.create(name='Advanced Timer', abbreviation='AT', level=2)

        # URLS
        self.cert_list_url = reverse('certification-list')
        self.cert_detail_url = reverse('certification-detail', kwargs={'pk': self.cert1.pk})

    def test_list_certs_unauthenticated(self):
        response = self.client.get(self.cert_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_cert_unauthenticated(self):
        response = self.client.get(self.cert_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_certs_authenticated(self):
        self.client.login(username='testuser_cert', password='testpassword123')
        response = self.client.get(self.cert_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], self.cert2.name) # 'Advanced Timer' (cert2) comes before 'Basic Scorer' (cert1)

    def test_retrieve_cert_authenticated(self):
        self.client.login(username='testuser_cert', password='testpassword123')
        response = self.client.get(self.cert_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.cert1.name)

    def test_create_cert_authenticated(self):
        self.client.login(username='testuser_cert', password='testpassword123')
        data = {'name': 'Expert Judge', 'abbreviation': 'EJ', 'level': 3, 'description': 'Top tier judge.'}
        response = self.client.post(self.cert_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Certification.objects.count(), 3)
        self.assertEqual(Certification.objects.latest('id').name, 'Expert Judge')

    def test_create_cert_missing_name_authenticated(self):
        self.client.login(username='testuser_cert', password='testpassword123')
        data = {'abbreviation': 'XX', 'level': 1} # Name is required
        response = self.client.post(self.cert_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_update_cert_authenticated(self):
        self.client.login(username='testuser_cert', password='testpassword123')
        updated_data = {'name': 'Certified Basic Scorer', 'abbreviation': 'CBS', 'level': 1, 'description': 'Updated desc.'}
        response = self.client.put(self.cert_detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cert1.refresh_from_db()
        self.assertEqual(self.cert1.name, 'Certified Basic Scorer')
        self.assertEqual(self.cert1.abbreviation, 'CBS')

    def test_partial_update_cert_authenticated(self):
        self.client.login(username='testuser_cert', password='testpassword123')
        patch_data = {'description': 'Patched cert description.'}
        response = self.client.patch(self.cert_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cert1.refresh_from_db()
        self.assertEqual(self.cert1.description, 'Patched cert description.')
        self.assertEqual(self.cert1.name, 'Basic Scorer') # Name should be unchanged

    def test_delete_cert_authenticated(self):
        self.client.login(username='testuser_cert', password='testpassword123')
        response = self.client.delete(self.cert_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Certification.objects.count(), 1)
        with self.assertRaises(Certification.DoesNotExist):
            Certification.objects.get(pk=self.cert1.pk)


class DivisionAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_div', password='testpassword123')
        self.league = League.objects.create(name='Parent League', founded_year=2000)
        self.div1 = Division.objects.create(name='North Division', league=self.league)
        self.div2 = Division.objects.create(name='South Division', league=self.league)

        # URLS
        self.div_list_url = reverse('division-list')
        self.div_detail_url = reverse('division-detail', kwargs={'pk': self.div1.pk})

    def test_list_divisions_unauthenticated(self):
        response = self.client.get(self.div_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_division_unauthenticated(self):
        response = self.client.get(self.div_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_divisions_authenticated(self):
        self.client.login(username='testuser_div', password='testpassword123')
        response = self.client.get(self.div_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Note: Default ordering in ViewSet is by league__name, name. So div1 should be first if names are N, S.
        self.assertEqual(response.data[0]['name'], self.div1.name) 

    def test_retrieve_division_authenticated(self):
        self.client.login(username='testuser_div', password='testpassword123')
        response = self.client.get(self.div_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.div1.name)

    def test_create_division_authenticated(self):
        self.client.login(username='testuser_div', password='testpassword123')
        data = {'name': 'East Division', 'league': self.league.pk, 'description': 'Newest division.'}
        response = self.client.post(self.div_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Division.objects.count(), 3)
        self.assertEqual(Division.objects.latest('id').name, 'East Division')

    def test_create_division_missing_name_authenticated(self):
        self.client.login(username='testuser_div', password='testpassword123')
        data = {'league': self.league.pk} # Name is required
        response = self.client.post(self.div_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_division_missing_league_authenticated(self):
        self.client.login(username='testuser_div', password='testpassword123')
        data = {'name': 'Orphan Division'} # League is required
        response = self.client.post(self.div_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('league', response.data)

    def test_update_division_authenticated(self):
        self.client.login(username='testuser_div', password='testpassword123')
        updated_data = {'name': 'Updated North Division', 'league': self.league.pk, 'description': 'Updated desc.'}
        response = self.client.put(self.div_detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.div1.refresh_from_db()
        self.assertEqual(self.div1.name, 'Updated North Division')
        self.assertEqual(self.div1.description, 'Updated desc.')

    def test_partial_update_division_authenticated(self):
        self.client.login(username='testuser_div', password='testpassword123')
        patch_data = {'description': 'Patched div description.'}
        response = self.client.patch(self.div_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.div1.refresh_from_db()
        self.assertEqual(self.div1.description, 'Patched div description.')
        self.assertEqual(self.div1.name, 'North Division') # Name should be unchanged

    def test_delete_division_authenticated(self):
        self.client.login(username='testuser_div', password='testpassword123')
        response = self.client.delete(self.div_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Division.objects.count(), 1)
        with self.assertRaises(Division.DoesNotExist):
            Division.objects.get(pk=self.div1.pk)


class TeamAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_team', password='testpassword123')
        self.league = League.objects.create(name='Test League for Teams', founded_year=2010)
        self.division = Division.objects.create(name='Test Division for Teams', league=self.league)
        self.team1 = Team.objects.create(name='Sharks', abbreviation='SHK', division=self.division, mascot='Sharky')
        self.team2 = Team.objects.create(name='Dolphins', abbreviation='DOL', division=self.division, mascot='Finny')

        # URLS
        self.team_list_url = reverse('team-list')
        self.team_detail_url = reverse('team-detail', kwargs={'pk': self.team1.pk})

    def test_list_teams_unauthenticated(self):
        response = self.client.get(self.team_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_team_unauthenticated(self):
        response = self.client.get(self.team_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_teams_authenticated(self):
        self.client.login(username='testuser_team', password='testpassword123')
        response = self.client.get(self.team_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Default ordering: 'division__league__name', 'division__name', 'name'
        # Assuming 'Dolphins' comes before 'Sharks' alphabetically
        self.assertEqual(response.data[0]['name'], self.team2.name) 

    def test_retrieve_team_authenticated(self):
        self.client.login(username='testuser_team', password='testpassword123')
        response = self.client.get(self.team_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.team1.name)

    def test_create_team_authenticated(self):
        self.client.login(username='testuser_team', password='testpassword123')
        data = {
            'name': 'Eagles',
            'abbreviation': 'EGL',
            'division': self.division.pk,
            'mascot': 'Screech'
        }
        response = self.client.post(self.team_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), 3)
        self.assertEqual(Team.objects.latest('id').name, 'Eagles')

    def test_create_team_missing_name_authenticated(self):
        self.client.login(username='testuser_team', password='testpassword123')
        data = {'abbreviation': 'XXX', 'division': self.division.pk} # Name is required
        response = self.client.post(self.team_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_team_missing_division_authenticated(self):
        self.client.login(username='testuser_team', password='testpassword123')
        data = {'name': 'Lone Wolves', 'abbreviation': 'LW'} # Division is required
        response = self.client.post(self.team_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('division', response.data)

    def test_update_team_authenticated(self):
        self.client.login(username='testuser_team', password='testpassword123')
        updated_data = {
            'name': 'Mighty Sharks',
            'abbreviation': 'MSHK',
            'division': self.division.pk,
            'mascot': 'Jaws',
            'address': '123 Ocean Drive'
        }
        response = self.client.put(self.team_detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.team1.refresh_from_db()
        self.assertEqual(self.team1.name, 'Mighty Sharks')
        self.assertEqual(self.team1.address, '123 Ocean Drive')

    def test_partial_update_team_authenticated(self):
        self.client.login(username='testuser_team', password='testpassword123')
        patch_data = {'mascot': 'Fin Diesel'}
        response = self.client.patch(self.team_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.team1.refresh_from_db()
        self.assertEqual(self.team1.mascot, 'Fin Diesel')
        self.assertEqual(self.team1.name, 'Sharks') # Name should be unchanged

    def test_delete_team_authenticated(self):
        self.client.login(username='testuser_team', password='testpassword123')
        response = self.client.delete(self.team_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Team.objects.count(), 1)
        with self.assertRaises(Team.DoesNotExist):
            Team.objects.get(pk=self.team1.pk)


class OfficialAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_official', password='testpassword123')
        self.league = League.objects.create(name='Official Test League', founded_year=2015)
        self.division = Division.objects.create(name='Official Test Division', league=self.league)
        self.team = Team.objects.create(name='Official Test Team', division=self.division)
        self.cert1 = Certification.objects.create(name='Referee Cert', abbreviation='REF', level=1)
        self.cert2 = Certification.objects.create(name='Umpire Cert', abbreviation='UMP', level=2)

        self.official1 = Official.objects.create(
            name='John Doe',
            email='john.doe@example.com',
            phone='555-1234',
            team=self.team,
            certification=self.cert1
        )

        self.official2 = Official.objects.create(
            name='Jane Smith',
            email='jane.smith@example.com',
            phone='555-5678',
            team=self.team,
            certification=self.cert2
        )

        # URLS
        self.official_list_url = reverse('official-list')
        self.official_detail_url = reverse('official-detail', kwargs={'pk': self.official1.pk})

    def test_list_officials_unauthenticated(self):
        response = self.client.get(self.official_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_official_unauthenticated(self):
        response = self.client.get(self.official_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_officials_authenticated(self):
        self.client.login(username='testuser_official', password='testpassword123')
        response = self.client.get(self.official_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Check both officials are in the response (order may vary)
        official_names = [item['name'] for item in response.data]
        self.assertIn(self.official1.name, official_names)
        self.assertIn(self.official2.name, official_names)

    def test_retrieve_official_authenticated(self):
        self.client.login(username='testuser_official', password='testpassword123')
        response = self.client.get(self.official_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.official1.name)
        self.assertEqual(response.data['certification'], self.cert1.pk)

    def test_create_official_authenticated(self):
        self.client.login(username='testuser_official', password='testpassword123')
        data = {
            'name': 'New Official',
            'email': 'new.official@example.com',
            'phone': '555-9999',
            'team': self.team.pk,
            'certification': self.cert1.pk
        }
        response = self.client.post(self.official_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Official.objects.count(), 3)
        new_official = Official.objects.get(name='New Official')
        self.assertEqual(new_official.certification, self.cert1)

    def test_create_official_missing_name_authenticated(self):
        self.client.login(username='testuser_official', password='testpassword123')
        data = {'email': 'fail@example.com', 'team': self.team.pk}
        response = self.client.post(self.official_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_official_missing_team_authenticated(self):
        self.client.login(username='testuser_official', password='testpassword123')
        data = {'name': 'No Team Official', 'email': 'noteam@example.com'}
        response = self.client.post(self.official_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('team', response.data)

    def test_update_official_authenticated(self):
        self.client.login(username='testuser_official', password='testpassword123')
        data = {
            'name': 'Updated John Doe',
            'email': 'updated.john@example.com',
            'phone': '555-1111',
            'team': self.team.pk,
            'certification': self.cert2.pk
        }
        response = self.client.put(self.official_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.official1.refresh_from_db()
        self.assertEqual(self.official1.name, 'Updated John Doe')
        self.assertEqual(self.official1.certification, self.cert2)

    def test_partial_update_official_authenticated(self):
        self.client.login(username='testuser_official', password='testpassword123')
        data = {'phone': '999-8888'}
        response = self.client.patch(self.official_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.official1.refresh_from_db()
        self.assertEqual(self.official1.phone, '999-8888')
        self.assertEqual(self.official1.name, 'John Doe')  # Name should be unchanged

    def test_delete_official_authenticated(self):
        self.client.login(username='testuser_official', password='testpassword123')
        response = self.client.delete(self.official_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Official.objects.count(), 1)
        with self.assertRaises(Official.DoesNotExist):
            Official.objects.get(pk=self.official1.pk)


            Pool.objects.get(pk=self.pool1.pk)


class AssignmentAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_assign', password='testpassword123')
        
        # Prerequisites
        self.league = League.objects.create(name='Assign Test League')
        self.division = Division.objects.create(name='Assign Test Division', league=self.league)
        self.team = Team.objects.create(name='Assign Test Team', division=self.division)
        self.cert = Certification.objects.create(name='Assign Cert', level=1)
        
        self.official1 = Official.objects.create(
            name='Official One',
            email='off1@example.com',
            team=self.team,
            certification=self.cert
        )
        self.official2 = Official.objects.create(
            name='Official Two',
            email='off2@example.com',
            team=self.team,
            certification=self.cert
        )
        
        today = timezone.now().date()
        self.meet = Meet.objects.create(name='Assign Test Meet', league=self.league, date=today, host_team=self.team)
        self.strategy = Strategy.objects.create(name=Strategy.STRATEGY_CHOICES[0][0])
        self.position1 = Position.objects.create(role='Referee', strategy=self.strategy, location='Pool deck')
        self.assignment1 = Assignment.objects.create(official=self.official1, meet=self.meet, role='Referee')
        self.assignment2 = Assignment.objects.create(official=self.official2, meet=self.meet, role='Starter')
        # Note: assigned_at is auto_now_add=True

        # URLS
        self.assignment_list_url = reverse('assignment-list')
        self.assignment_detail_url = reverse('assignment-detail', kwargs={'pk': self.assignment1.pk})

    def test_list_assignments_unauthenticated(self):
        response = self.client.get(self.assignment_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_assignment_unauthenticated(self):
        response = self.client.get(self.assignment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_assignments_authenticated(self):
        self.client.login(username='testuser_assign', password='testpassword123')
        response = self.client.get(self.assignment_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Check both officials are in the response (order may vary)
        official_ids = [item['official'] for item in response.data]
        self.assertIn(self.official1.pk, official_ids)
        self.assertIn(self.official2.pk, official_ids)

    def test_retrieve_assignment_authenticated(self):
        self.client.login(username='testuser_assign', password='testpassword123')
        response = self.client.get(self.assignment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['official'], self.official1.pk)
        self.assertEqual(response.data['role'], 'Referee')
        self.assertIsNotNone(response.data['assigned_at'])

    def test_create_assignment_authenticated(self):
        self.client.login(username='testuser_assign', password='testpassword123')
        data = {
            'official': self.official2.pk,
            'meet': self.meet.pk,
            'role': 'Stroke Judge',
            'notes': 'Second assignment created via API'
        }
        response = self.client.post(self.assignment_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Assignment.objects.count(), 3)
        new_assignment = Assignment.objects.latest('id')
        self.assertEqual(new_assignment.official, self.official2)
        self.assertEqual(new_assignment.role, 'Stroke Judge')

    def test_create_assignment_missing_official_authenticated(self):
        self.client.login(username='testuser_assign', password='testpassword123')
        data = {'meet': self.meet.pk, 'role': 'Referee'}
        response = self.client.post(self.assignment_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('official', response.data)

    def test_create_assignment_missing_meet_authenticated(self):
        self.client.login(username='testuser_assign', password='testpassword123')
        data = {'official': self.official1.pk, 'role': 'Referee'}
        response = self.client.post(self.assignment_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('meet', response.data)

    def test_create_assignment_missing_position_authenticated(self):
        self.client.login(username='testuser_assign', password='testpassword123')
        data = {'official': self.official1.pk, 'meet': self.meet.pk}
        response = self.client.post(self.assignment_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)

    def test_update_assignment_authenticated(self):
        self.client.login(username='testuser_assign', password='testpassword123')
        # Assignments are often more about creation/deletion than updates of core fields.
        # Here we'll update the 'notes' field as an example.
        # Changing official, meet, or position might imply a new assignment rather than updating an existing one.
        updated_data = {
            'official': self.official1.pk, # Must provide FKs for PUT
            'meet': self.meet.pk,
            'role': 'Referee',
            'notes': 'Updated notes for assignment 1'
        }
        response = self.client.put(self.assignment_detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assignment1.refresh_from_db()
        self.assertEqual(self.assignment1.notes, 'Updated notes for assignment 1')

    def test_partial_update_assignment_authenticated(self):
        self.client.login(username='testuser_assign', password='testpassword123')
        patch_data = {'notes': 'Patched notes for assignment 1'}
        response = self.client.patch(self.assignment_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assignment1.refresh_from_db()
        self.assertEqual(self.assignment1.notes, 'Patched notes for assignment 1')

    def test_delete_assignment_authenticated(self):
        self.client.login(username='testuser_assign', password='testpassword123')
        response = self.client.delete(self.assignment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Assignment.objects.count(), 1)
        with self.assertRaises(Assignment.DoesNotExist):
            Assignment.objects.get(pk=self.assignment1.pk)


class EventAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_event', password='testpassword123')
        self.league = League.objects.create(name='Event Test League')
        self.division = Division.objects.create(name='Event Test Division', league=self.league)
        self.team = Team.objects.create(name='Event Test Team', division=self.division)
        today = timezone.now().date()
        self.meet = Meet.objects.create(name='Event Test Meet', league=self.league, date=today, host_team=self.team)
        self.pool = Pool.objects.create(name='Event Test Pool', team=self.team, length=25, units='Meters', lanes=8)

        now_time = timezone.now()
        self.event1 = Event.objects.create(
            event_number=1,
            name='Freestyle 100',
            description='100 meter freestyle',
            meet_type='dual',
            gender='male'
        )
        self.event2 = Event.objects.create(
            event_number=2,
            name='Backstroke 50',
            description='50 meter backstroke',
            meet_type='dual',
            gender='female'
        )

        # URLS
        self.event_list_url = reverse('event-list')
        self.event_detail_url = reverse('event-detail', kwargs={'pk': self.event1.pk})

    def test_list_events_unauthenticated(self):
        response = self.client.get(self.event_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_event_unauthenticated(self):
        response = self.client.get(self.event_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_events_authenticated(self):
        self.client.login(username='testuser_event', password='testpassword123')
        response = self.client.get(self.event_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Default ordering: 'meet__name', 'session_number', 'event_number'
        self.assertEqual(response.data[0]['event_number'], self.event1.event_number)

    def test_retrieve_event_authenticated(self):
        self.client.login(username='testuser_event', password='testpassword123')
        response = self.client.get(self.event_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['event_number'], self.event1.event_number)
        self.assertEqual(response.data['name'], self.event1.name)

    def test_create_event_authenticated(self):
        self.client.login(username='testuser_event', password='testpassword123')
        data = {
            'event_number': 3,
            'name': 'Butterfly 200',
            'description': '200 meter butterfly',
            'meet_type': 'dual',
            'gender': 'female'
        }
        response = self.client.post(self.event_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 3)
        new_event = Event.objects.get(event_number=3)
        self.assertEqual(new_event.event_number, 3)
        self.assertEqual(new_event.name, 'Butterfly 200')

    def test_create_event_missing_name_authenticated(self):
        self.client.login(username='testuser_event', password='testpassword123')
        data = {'event_number': 4, 'description': '100 meter breaststroke'}
        response = self.client.post(self.event_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_event_invalid_field_value(self):
        self.client.login(username='testuser_event', password='testpassword123')
        data = {
            'event_number': 4,
            'name': 'IM 400',
            'description': '400 meter individual medley',
            'meet_type': 'invalid_type',  # Invalid choice
            'gender': 'female'
        }
        response = self.client.post(self.event_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('meet_type', response.data)

    def test_update_event_authenticated(self):
        self.client.login(username='testuser_event', password='testpassword123')
        data = {
            'event_number': self.event1.event_number,
            'name': 'Medley Relay 200',
            'description': '200 meter medley relay',
            'meet_type': 'divisional',
            'gender': 'female'
        }
        response = self.client.put(self.event_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event1.refresh_from_db()
        self.assertEqual(self.event1.name, 'Medley Relay 200')
        self.assertEqual(self.event1.meet_type, 'divisional')

    def test_partial_update_event_authenticated(self):
        self.client.login(username='testuser_event', password='testpassword123')
        data = {'description': 'Updated description'}
        response = self.client.patch(self.event_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event1.refresh_from_db()
        self.assertEqual(self.event1.description, 'Updated description')

    def test_delete_event_authenticated(self):
        self.client.login(username='testuser_event', password='testpassword123')
        response = self.client.delete(self.event_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Event.objects.count(), 1)
        with self.assertRaises(Event.DoesNotExist):
            Event.objects.get(pk=self.event1.pk)


class StrategyAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_strategy', password='testpassword123')
        # Ensure a clean slate for strategy choices if tests run multiple times or in parallel
        Strategy.objects.all().delete()
        self.strategy1 = Strategy.objects.create(name=Strategy.STRATEGY_CHOICES[0][0])  # QUADRANTS
        self.strategy2 = Strategy.objects.create(name=Strategy.STRATEGY_CHOICES[1][0])  # SIDES

        # URLS
        self.strategy_list_url = reverse('strategy-list')
        self.strategy_detail_url = reverse('strategy-detail', kwargs={'pk': self.strategy1.pk})

    def test_list_strategies_unauthenticated(self):
        response = self.client.get(self.strategy_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_strategy_unauthenticated(self):
        response = self.client.get(self.strategy_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_strategies_authenticated(self):
        self.client.login(username='testuser_strategy', password='testpassword123')
        response = self.client.get(self.strategy_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Default ordering is by name ('QUADRANTS' before 'SIDES')
        self.assertEqual(response.data[0]['name'], self.strategy1.name)  # QUADRANTS
        self.assertEqual(response.data[1]['name'], self.strategy2.name)  # SIDES

    def test_retrieve_strategy_authenticated(self):
        self.client.login(username='testuser_strategy', password='testpassword123')
        response = self.client.get(self.strategy_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.strategy1.name)
        # 'is_default' is not a field on the Strategy model or serializer

    def test_create_strategy_invalid_name_authenticated(self):
        self.client.login(username='testuser_strategy', password='testpassword123')
        data = {'name': 'INVALID_STRATEGY_NAME'}
        response = self.client.post(self.strategy_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Strategy.objects.count(), 2)  # No new strategy should be created
        self.assertIn('name', response.data) # Expect error message for name field due to invalid choice

    def test_create_strategy_duplicate_name_authenticated(self):
        self.client.login(username='testuser_strategy', password='testpassword123')
        data = {'name': self.strategy1.name} # Try to create 'QUADRANTS' again
        response = self.client.post(self.strategy_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Strategy.objects.count(), 2)
        self.assertIn('name', response.data) # Expect error for uniqueness constraint

    def test_create_strategy_missing_name_authenticated(self):
        self.client.login(username='testuser_strategy', password='testpassword123')
        data = {} # Missing name
        response = self.client.post(self.strategy_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_update_strategy_to_duplicate_name_authenticated(self):
        self.client.login(username='testuser_strategy', password='testpassword123')
        # Try to update strategy1's name to strategy2's name ('SIDES')
        updated_data = {'name': self.strategy2.name}
        response = self.client.put(self.strategy_detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) # 'SIDES' is already taken
        self.strategy1.refresh_from_db()
        self.assertEqual(self.strategy1.name, Strategy.STRATEGY_CHOICES[0][0])  # Name should remain 'QUADRANTS'
        self.assertIn('name', response.data)

    def test_update_strategy_to_invalid_name_authenticated(self):
        self.client.login(username='testuser_strategy', password='testpassword123')
        updated_data = {'name': 'INVALID_UPDATE_NAME'}
        response = self.client.put(self.strategy_detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.strategy1.refresh_from_db()
        self.assertEqual(self.strategy1.name, Strategy.STRATEGY_CHOICES[0][0])
        self.assertIn('name', response.data)

    def test_partial_update_strategy_to_invalid_name_authenticated(self):
        self.client.login(username='testuser_strategy', password='testpassword123')
        patch_data = {'name': 'INVALID_PATCH_NAME'}
        response = self.client.patch(self.strategy_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.strategy1.refresh_from_db()
        self.assertEqual(self.strategy1.name, Strategy.STRATEGY_CHOICES[0][0])  # Name should be unchanged
        self.assertIn('name', response.data)

    def test_delete_strategy_authenticated(self):
        self.client.login(username='testuser_strategy', password='testpassword123')
        response = self.client.delete(self.strategy_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Strategy.objects.count(), 1)
        with self.assertRaises(Strategy.DoesNotExist):
            Strategy.objects.get(pk=self.strategy1.pk)


class PositionAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_position', password='testpassword123')
        self.league = League.objects.create(name='Position Test League')
        self.division = Division.objects.create(name='Position Test Division', league=self.league)
        self.team = Team.objects.create(name='Position Test Team', division=self.division)
        today = timezone.now().date()
        self.meet = Meet.objects.create(name='Position Test Meet', league=self.league, date=today, host_team=self.team)
        # Strategy only accepts predefined choices, not custom names
        self.strategy = Strategy.objects.create(name=Strategy.STRATEGY_CHOICES[0][0])

        self.position1 = Position.objects.create(
            role='Referee',
            strategy=self.strategy,
            location='Pool deck'
        )
        self.position2 = Position.objects.create(
            role='Starter',
            strategy=self.strategy,
            location='Starting blocks'
        )

        # URLS
        self.position_list_url = reverse('position-list')
        self.position_detail_url = reverse('position-detail', kwargs={'pk': self.position1.pk})

    def test_list_positions_unauthenticated(self):
        response = self.client.get(self.position_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_position_unauthenticated(self):
        response = self.client.get(self.position_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_positions_authenticated(self):
        self.client.login(username='testuser_position', password='testpassword123')
        response = self.client.get(self.position_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Default ordering is by role
        self.assertEqual(response.data[0]['role'], self.position1.role) # Referee
        self.assertEqual(response.data[1]['role'], self.position2.role) # Starter

    def test_retrieve_position_authenticated(self):
        self.client.login(username='testuser_position', password='testpassword123')
        response = self.client.get(self.position_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], self.position1.role)
        self.assertEqual(response.data['strategy'], self.strategy.pk)
        self.assertEqual(response.data['location'], self.position1.location)

    def test_create_position_authenticated(self):
        self.client.login(username='testuser_position', password='testpassword123')
        data = {
            'role': 'Chief Judge',
            'strategy': self.strategy.pk,
            'location': 'Finish line'
        }
        response = self.client.post(self.position_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Position.objects.count(), 3)
        new_position = Position.objects.get(role='Chief Judge')
        self.assertEqual(new_position.strategy, self.strategy)

    def test_create_position_missing_role_authenticated(self):
        self.client.login(username='testuser_position', password='testpassword123')
        data = {
            'strategy': self.strategy.pk,
            'location': 'Finish line'
        }
        response = self.client.post(self.position_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)

    def test_create_position_missing_strategy_authenticated(self):
        self.client.login(username='testuser_position', password='testpassword123')
        data = {'role': 'Timer', 'location': 'Finish line'}
        response = self.client.post(self.position_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('strategy', response.data)

    def test_update_position_authenticated(self):
        self.client.login(username='testuser_position', password='testpassword123')
        data = {
            'role': 'Head Referee',
            'strategy': self.strategy.pk,
            'location': 'Updated location'
        }
        response = self.client.put(self.position_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.position1.refresh_from_db()
        self.assertEqual(self.position1.role, 'Head Referee')
        self.assertEqual(self.position1.location, 'Updated location')

    def test_partial_update_position_authenticated(self):
        self.client.login(username='testuser_position', password='testpassword123')
        patch_data = {'location': 'Updated location'}
        response = self.client.patch(self.position_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.position1.refresh_from_db()
        self.assertEqual(self.position1.location, 'Updated location')
        self.assertEqual(self.position1.role, 'Referee') # Role should be unchanged

    def test_delete_position_authenticated(self):
        self.client.login(username='testuser_position', password='testpassword123')
        response = self.client.delete(self.position_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Position.objects.count(), 1)
        with self.assertRaises(Position.DoesNotExist):
            Position.objects.get(pk=self.position1.pk)


class UserLeagueAdminAPITests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='adminleagueuser', password='testpassword123', is_staff=True) # Staff for easier testing
        self.target_user = User.objects.create_user(username='targetleagueuser', password='testpassword123')
        self.other_user = User.objects.create_user(username='otherleagueuser', password='testpassword456')
        
        self.league1 = League.objects.create(name='ULA Test League 1')
        self.league2 = League.objects.create(name='ULA Test League 2')

        self.ula1 = UserLeagueAdmin.objects.create(user=self.target_user, league=self.league1, role=UserLeagueAdmin.RoleChoices.ADMIN)

        # URLS
        self.ula_list_url = reverse('userleagueadmin-list')
        self.ula_detail_url = reverse('userleagueadmin-detail', kwargs={'pk': self.ula1.pk})

    def test_list_ula_unauthenticated(self):
        response = self.client.get(self.ula_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_ula_unauthenticated(self):
        response = self.client.get(self.ula_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_ula_authenticated(self):
        self.client.login(username='adminleagueuser', password='testpassword123')
        response = self.client.get(self.ula_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.target_user.pk)
        self.assertEqual(response.data[0]['league'], self.league1.pk)

    def test_retrieve_ula_authenticated(self):
        self.client.login(username='adminleagueuser', password='testpassword123')
        response = self.client.get(self.ula_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.target_user.pk)
        self.assertEqual(response.data['league'], self.league1.pk)
        self.assertEqual(response.data['role'], UserLeagueAdmin.RoleChoices.ADMIN)

    def test_create_ula_authenticated(self):
        self.client.login(username='adminleagueuser', password='testpassword123')
        data = {
            'user': self.other_user.pk,
            'league': self.league2.pk,
            'role': UserLeagueAdmin.RoleChoices.EDITOR
        }
        response = self.client.post(self.ula_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserLeagueAdmin.objects.count(), 2)
        new_ula = UserLeagueAdmin.objects.get(user=self.other_user, league=self.league2)
        self.assertEqual(new_ula.role, UserLeagueAdmin.RoleChoices.EDITOR)

    def test_create_ula_missing_user_authenticated(self):
        self.client.login(username='adminleagueuser', password='testpassword123')
        data = {'league': self.league1.pk, 'role': UserLeagueAdmin.RoleChoices.VIEWER}
        response = self.client.post(self.ula_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user', response.data)

    def test_create_ula_missing_league_authenticated(self):
        self.client.login(username='adminleagueuser', password='testpassword123')
        data = {'user': self.target_user.pk, 'role': UserLeagueAdmin.RoleChoices.VIEWER}
        response = self.client.post(self.ula_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('league', response.data)
    
    def test_create_ula_invalid_role_authenticated(self):
        self.client.login(username='adminleagueuser', password='testpassword123')
        data = {'user': self.other_user.pk, 'league': self.league2.pk, 'role': 'INVALID_ROLE'}
        response = self.client.post(self.ula_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)

    def test_update_ula_authenticated(self):
        self.client.login(username='adminleagueuser', password='testpassword123')
        updated_data = {
            'user': self.target_user.pk, # User and League typically don't change for an existing ULA
            'league': self.league1.pk,
            'role': UserLeagueAdmin.RoleChoices.VIEWER # Change role
        }
        response = self.client.put(self.ula_detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ula1.refresh_from_db()
        self.assertEqual(self.ula1.role, UserLeagueAdmin.RoleChoices.VIEWER)

    def test_partial_update_ula_authenticated(self):
        self.client.login(username='adminleagueuser', password='testpassword123')
        patch_data = {'role': UserLeagueAdmin.RoleChoices.EDITOR}
        response = self.client.patch(self.ula_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ula1.refresh_from_db()
        self.assertEqual(self.ula1.role, UserLeagueAdmin.RoleChoices.EDITOR)

    def test_delete_ula_authenticated(self):
        self.client.login(username='adminleagueuser', password='testpassword123')
        response = self.client.delete(self.ula_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(UserLeagueAdmin.objects.count(), 0)
        with self.assertRaises(UserLeagueAdmin.DoesNotExist):
            UserLeagueAdmin.objects.get(pk=self.ula1.pk)
