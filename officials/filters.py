import django_filters
from django import forms
from .models import Event, Meet, Official, Certification, Position, Strategy, League, Division, Team
from django.db.models import Min, Max

class EventFilter(django_filters.FilterSet):
    """Filter for Event model."""
    
    event_number = django_filters.NumberFilter(
        field_name='event_number',
        lookup_expr='exact',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name'})
    )
    
    meet_type = django_filters.ChoiceFilter(
        field_name='meet_type',
        choices=Event.MEET_TYPE_CHOICES,
        empty_label='All Meet Types',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    gender = django_filters.ChoiceFilter(
        field_name='gender',
        choices=Event.GENDER_CHOICES,
        empty_label='All Genders',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Event
        fields = ['event_number', 'name', 'meet_type', 'gender']

class PositionFilter(django_filters.FilterSet):
    """Filter for Position model."""
    
    role = django_filters.CharFilter(
        field_name='role',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by role title'})
    )
    
    strategy = django_filters.ModelChoiceFilter(
        field_name='strategy',
        queryset=Strategy.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Strategies"
    )
    
    location = django_filters.CharFilter(
        field_name='location',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Filter by location'})
    )
    
    class Meta:
        model = Position
        fields = ['role', 'strategy', 'location']

class LeagueFilter(django_filters.FilterSet):
    """Filter for League model."""
    
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by league name'})
    )
    
    
    has_divisions = django_filters.BooleanFilter(
        method='filter_has_divisions',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Has Divisions'
    )
    
    def filter_has_divisions(self, queryset, name, value):
        if value:  # If checkbox is checked
            return queryset.filter(divisions__isnull=False).distinct()
        return queryset  # If not checked, return all
    
    class Meta:
        model = League
        fields = ['name', 'has_divisions']

class DivisionFilter(django_filters.FilterSet):
    """Filter for Division model."""
    
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by division name'})
    )

    description = django_filters.CharFilter(
        field_name='description',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by description'}),
        label='Description'
    )

    league = django_filters.ModelChoiceFilter(
        field_name='league',
        queryset=League.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="All Leagues"
    )
    
    has_teams = django_filters.BooleanFilter(
        method='filter_has_teams',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Has Teams'
    )
    
    def filter_has_teams(self, queryset, name, value):
        if value:  # If checkbox is checked
            return queryset.filter(teams__isnull=False).distinct()
        return queryset  # If not checked, return all
    
    class Meta:
        model = Division
        fields = ['name', 'description', 'league', 'has_teams']


class TeamFilter(django_filters.FilterSet):
    """Filter for Team model."""
    
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by team name'})
    )
    
    division = django_filters.ModelChoiceFilter(
        field_name='division',
        queryset=Division.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="All Divisions"
    )
    
    abbreviation = django_filters.CharFilter(
        field_name='abbreviation',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by abbreviation'})
    )
    
    has_officials = django_filters.BooleanFilter(
        method='filter_has_officials',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Has Officials'
    )
    
    def filter_has_officials(self, queryset, name, value):
        if value:  # If checkbox is checked
            return queryset.filter(officials__isnull=False).distinct()
        return queryset  # If not checked, return all
    
    class Meta:
        model = Team
        fields = ['name', 'division', 'abbreviation', 'has_officials']


class CertificationFilter(django_filters.FilterSet):
    """Filter for Certification model."""
    
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by certification name'})
    )
    
    abbreviation = django_filters.CharFilter(
        field_name='abbreviation',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by abbreviation'})
    )
    
    level = django_filters.NumberFilter(
        field_name='level',
        lookup_expr='exact',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Filter by level'})
    )
    
    level_min = django_filters.NumberFilter(
        field_name='level',
        lookup_expr='gte',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min level'})
    )
    
    level_max = django_filters.NumberFilter(
        field_name='level',
        lookup_expr='lte',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max level'})
    )
    
    class Meta:
        model = Certification
        fields = ['name', 'abbreviation', 'level', 'level_min', 'level_max']


class StrategyFilter(django_filters.FilterSet):
    """Filter for Strategy model."""
    
    name = django_filters.ChoiceFilter(
        field_name='name',
        choices=Strategy.STRATEGY_CHOICES,
        empty_label='All Strategies',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    has_positions = django_filters.BooleanFilter(
        method='filter_has_positions',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Has Positions'
    )
    
    def filter_has_positions(self, queryset, name, value):
        if value:  # If checkbox is checked
            return queryset.filter(positions__isnull=False).distinct()
        return queryset  # If not checked, return all
    
    class Meta:
        model = Strategy
        fields = ['name', 'has_positions']


# Existing filters that needed to be improved
class MeetFilter(django_filters.FilterSet):
    """Filter for Meet model."""
    
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by meet name'})
    )
    
    date_min = django_filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Date from'
    )
    
    date_max = django_filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Date to'
    )
    
    league = django_filters.ModelChoiceFilter(
        field_name='league',
        queryset=League.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="All Leagues"
    )
    
    meet_type = django_filters.ChoiceFilter(
        field_name='meet_type',
        choices=Meet.MEET_TYPE_CHOICES,
        empty_label='All Meet Types',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Meet
        fields = ['name', 'date_min', 'date_max', 'league', 'meet_type']


class OfficialFilter(django_filters.FilterSet):
    """Filter for Official model."""
    
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name'})
    )
    
    certification = django_filters.ModelChoiceFilter(
        field_name='certification',
        queryset=Certification.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="All Certifications"
    )
    
    team = django_filters.ModelChoiceFilter(
        field_name='team',
        queryset=Team.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="All Teams"
    )
    
    active = django_filters.BooleanFilter(
        field_name='active',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Active Officials Only'
    )
    
    proficiency = django_filters.ChoiceFilter(
        field_name='proficiency',
        choices=Official.PROFICIENCY_CHOICES,
        empty_label='All Proficiency Levels',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Official
        fields = ['name', 'certification', 'team', 'active', 'proficiency']
