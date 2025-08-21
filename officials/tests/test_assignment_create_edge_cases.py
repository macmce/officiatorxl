from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from officials.models import League, Division, Team, Pool, Meet, Official, Certification
from datetime import date, timedelta

User = get_user_model()

class AssignmentCreateEdgeCasesTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Users
        self.user = User.objects.create_user(
            username='edgeuser', email='edge@example.com', password='edgepass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', email='other@example.com', password='otherpass123'
        )
        # Leagues/divisions/teams
        self.league = League.objects.create(name='Edge League', description='desc', founded_year=2020)
        self.division = Division.objects.create(name='Edge Div', description='desc', league=self.league)
        self.team = Team.objects.create(name='Edge Team', abbreviation='ET', mascot='Eels', division=self.division)
        self.pool = Pool.objects.create(name='Edge Pool', address='123 St', length=25, units='meters', lanes=6, team=self.team)
        self.league.users.add(self.user)

        self.other_league = League.objects.create(name='Other L', description='desc', founded_year=2021)
        self.other_division = Division.objects.create(name='Other Div', description='desc', league=self.other_league)
        self.other_team = Team.objects.create(name='Other Team', abbreviation='OT', mascot='Owls', division=self.other_division)
        self.other_pool = Pool.objects.create(name='Other Pool', address='456 St', length=25, units='yards', lanes=8, team=self.other_team)
        self.other_league.users.add(self.other_user)

        # Meet in user's league
        self.meet = Meet.objects.create(
            name='Edge Meet',
            date=date.today() + timedelta(days=7),
            league=self.league,
            host_team=self.team,
            pool=self.pool,
            meet_type='dual'
        )
        self.meet.participating_teams.add(self.team)

        # Other league meet
        self.other_meet = Meet.objects.create(
            name='Other Meet',
            date=date.today() + timedelta(days=7),
            league=self.other_league,
            host_team=self.other_team,
            pool=self.other_pool,
            meet_type='dual'
        )
        self.other_meet.participating_teams.add(self.other_team)

        # Official and certification
        self.cert = Certification.objects.create(name='Edge Cert', abbreviation='EC', description='desc', level=1)
        self.official = Official.objects.create(
            name='Edge Official', email='edgeoff@example.com', phone='555-111-2222',
            certification=self.cert, team=self.team, active=True, proficiency='Intermediate'
        )

    def login(self):
        self.client.login(username='edgeuser', password='edgepass123')

    def test_create_with_existing_official_requires_role(self):
        self.login()
        # Missing role should be invalid and re-render 200
        data = {
            'meet': self.meet.id,
            'official': self.official.id,
            'role': '',
        }
        resp = self.client.post(reverse('assignment_create'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Certification is required', status_code=200)

    def test_create_with_new_official_minimal_fields(self):
        self.login()
        data = {
            'meet': self.meet.id,
            'official': '',
            'new_official_name': 'Brand New Official',
            'new_official_email': 'new@example.com',
            'new_official_team': self.team.id,
            'new_official_certification': self.cert.id,
            'new_official_active': 'on',
            'new_official_proficiency': 'Intermediate',
            'role': '',  # allowed empty for new official
            'notes': 'created via new official path',
        }
        resp = self.client.post(reverse('assignment_create'), data)
        # Should redirect to meet detail on success
        self.assertEqual(resp.status_code, 302)

    def test_create_rejects_both_existing_and_new_official(self):
        self.login()
        data = {
            'meet': self.meet.id,
            'official': self.official.id,
            'new_official_name': 'Should Fail',
            'new_official_team': self.team.id,
            'new_official_certification': self.cert.id,
            'role': 'Referee',
        }
        resp = self.client.post(reverse('assignment_create'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'either select an existing official or enter a new official', status_code=200)

    def test_permission_denied_for_other_league_meet(self):
        self.login()
        data = {
            'meet': self.other_meet.id,
            'official': self.official.id,
            'role': 'Referee',
        }
        resp = self.client.post(reverse('assignment_create'), data)
        # Permission check should redirect back to assignment list
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('assignment_list'), resp.url)

    def test_preselected_meet_path_get_and_post(self):
        self.login()
        # GET with preselected meet in path
        resp_get = self.client.get(reverse('assignment_create_for_meet', args=[self.meet.id]))
        self.assertEqual(resp_get.status_code, 200)
        # POST without meet field should still work because meet is preselected/disabled
        data = {
            'official': self.official.id,
            'role': 'Starter',
            'notes': 'preselected path',
        }
        resp_post = self.client.post(reverse('assignment_create_for_meet', args=[self.meet.id]), data)
        self.assertEqual(resp_post.status_code, 302)
