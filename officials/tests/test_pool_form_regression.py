from django.test import TestCase
from officials.forms import PoolForm
from officials.models import Team, League, Division

class PoolFormRegressionTest(TestCase):
    def setUp(self):
        league = League.objects.create(name='L', description='d', founded_year=2000)
        division = Division.objects.create(name='D', description='d', league=league)
        self.team = Team.objects.create(name='T', abbreviation='T', mascot='M', division=division)

    def test_team_field_present_and_required(self):
        form = PoolForm()
        self.assertIn('team', form.fields)
        # team is required by default ModelForm unless overridden
        self.assertTrue(form.fields['team'].required)

    def test_valid_submission_succeeds(self):
        data = {
            'name': 'P',
            'address': '123 St',
            'length': 25,
            'units': 'Meters',
            'lanes': 6,
            'team': self.team.id,
        }
        form = PoolForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_missing_team_is_invalid(self):
        data = {
            'name': 'P',
            'address': '123 St',
            'length': 25,
            'units': 'Meters',
            'lanes': 6,
        }
        form = PoolForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('team', form.errors)
