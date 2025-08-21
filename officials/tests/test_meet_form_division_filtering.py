from django.test import TestCase
from officials.forms import MeetForm
from officials.models import League, Division
import datetime

class MeetFormDivisionFilteringTest(TestCase):
    def setUp(self):
        self.league1 = League.objects.create(name='League A', description='A', founded_year=2000)
        self.league2 = League.objects.create(name='League B', description='B', founded_year=2001)
        self.div_a1 = Division.objects.create(name='A1', description='d', league=self.league1)
        self.div_a2 = Division.objects.create(name='A2', description='d', league=self.league1)
        self.div_b1 = Division.objects.create(name='B1', description='d', league=self.league2)

    def test_initial_single_league_preselects_and_filters_divisions(self):
        # With exactly one league in DB, form should preselect and filter divisions
        League.objects.exclude(id=self.league1.id).delete()
        form = MeetForm()
        # division queryset should be only for the single league
        self.assertQuerySetEqual(
            form.fields['division'].queryset.order_by('id'),
            Division.objects.filter(league=self.league1).order_by('id'),
            transform=lambda x: x
        )
        # division is optional
        self.assertFalse(form.fields['division'].required)
        # start_time has initial default and is not required
        self.assertFalse(form.fields['start_time'].required)
        self.assertIsInstance(form.fields['start_time'].initial, datetime.time)
        # date has initial default (next Saturday)
        self.assertIsInstance(form.fields['date'].initial, datetime.date)

    def test_submitted_league_filters_divisions(self):
        data = {'league': str(self.league2.id), 'name': 'X', 'meet_type': 'dual', 'host_team': '', 'pool': ''}
        form = MeetForm(data=data)
        # division queryset should be filtered by submitted league
        self.assertQuerySetEqual(
            form.fields['division'].queryset.order_by('id'),
            Division.objects.filter(league=self.league2).order_by('id'),
            transform=lambda x: x
        )

    def test_no_league_has_empty_division_queryset(self):
        form = MeetForm()
        # when multiple leagues and no selection, division queryset should be empty
        self.assertEqual(form.fields['division'].queryset.count(), 0)
