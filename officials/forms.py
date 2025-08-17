from django import forms
import datetime
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, modelformset_factory

from .models import League, Division, Team, Position, Meet, Assignment, Pool, Event, Strategy, Certification, Official, EventPosition


class OfficialImportForm(forms.Form):
    """Form for importing officials from Excel file."""
    excel_file = forms.FileField(
        label='Excel File', 
        help_text='Upload an Excel file with officials data. Required columns: name, email. Optional columns: phone, proficiency, certification.')


class CertificationForm(forms.ModelForm):
    """Form for creating and updating certifications."""
    class Meta:
        model = Certification
        fields = ['name', 'abbreviation', 'description', 'level']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class LeagueForm(forms.ModelForm):
    """Form for creating and updating leagues."""
    class Meta:
        model = League
        fields = ['name', 'description', 'founded_year', 'logo', 'users']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'founded_year': forms.NumberInput(attrs={'min': 1900, 'max': 2100}),
        }


class DivisionForm(forms.ModelForm):
    """Form for creating and updating divisions."""
    class Meta:
        model = Division
        fields = ['name', 'description', 'league']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class TeamForm(forms.ModelForm):
    """Form for creating and updating teams."""
    class Meta:
        model = Team
        fields = ['name', 'abbreviation', 'mascot', 'division', 'logo', 'address', 'website']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'abbreviation': forms.TextInput(attrs={'maxlength': 10}),
        }


class PoolForm(forms.ModelForm):
    """Form for creating and updating pools."""
    class Meta:
        model = Pool
        fields = ['name', 'address', 'length', 'units', 'lanes', 'bidirectional', 'team']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'length': forms.NumberInput(attrs={'min': 10, 'max': 100}),
            'lanes': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }


class OfficialForm(forms.ModelForm):
    """Form for creating and updating officials."""
    class Meta:
        model = Official
        fields = ['name', 'email', 'phone', 'certification', 'team', 'active', 'proficiency']
        widgets = {
            'proficiency': forms.Select(),
        }


class PoolSelectWidget(forms.Select):
    """Custom widget for pool selection that includes address data in options."""
    
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value and value != '':
            try:
                # Handle ModelChoiceIteratorValue objects
                if hasattr(value, 'value'):
                    pool_id = value.value
                else:
                    pool_id = value
                
                from .models import Pool
                pool = Pool.objects.get(pk=pool_id)
                option['attrs']['data-address'] = pool.address or ''
            except (Pool.DoesNotExist, ValueError, TypeError):
                option['attrs']['data-address'] = ''
        else:
            option['attrs']['data-address'] = ''
        return option


class MeetForm(forms.ModelForm):
    """Form for creating and updating meets."""
    class Meta:
        model = Meet
        fields = ['league', 'division', 'date', 'start_time', 'host_team', 'pool', 'name', 'meet_type', 'participating_teams']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'meet_type': forms.Select(),
            'name': forms.TextInput(attrs={'placeholder': 'Enter meet name'}),
            'pool': PoolSelectWidget(),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add a hidden field to track whether name field is auto-generated
        self.auto_generated_name = True
        
        # Make name field required
        self.fields['name'].required = True
        
        # If only one league exists and none provided, preload it
        if not self.data.get('league') and not getattr(self.instance, 'league_id', None):
            league_qs = League.objects.all()
            if league_qs.count() == 1:
                only_league = league_qs.first()
                self.initial['league'] = only_league.id
                # Set division queryset to this league since league is preselected
                self.fields['division'].queryset = Division.objects.filter(league=only_league)
        
        # Set division queryset based on league
        if self.instance and self.instance.pk and self.instance.league:
            # Editing existing meet - filter by instance league
            self.fields['division'].queryset = Division.objects.filter(league=self.instance.league)
        elif self.data and self.data.get('league'):
            # Form submission with league data - filter by submitted league
            try:
                league_id = int(self.data.get('league'))
                self.fields['division'].queryset = Division.objects.filter(league_id=league_id)
            except (ValueError, TypeError):
                self.fields['division'].queryset = Division.objects.none()
        else:
            # New meet form load - start with empty division queryset
            self.fields['division'].queryset = Division.objects.none()
        
        # Set division field properties
        self.fields['division'].empty_label = "Select a division"
        self.fields['division'].required = False  # Allow optional division
        
        # Default start time to 08:30 if not provided
        if not self.initial.get('start_time') and not self.data.get('start_time'):
            self.fields['start_time'].initial = datetime.time(8, 30)
        
        # Default date to the next Saturday if not provided
        if not self.initial.get('date') and not self.data.get('date'):
            today = datetime.date.today()
            # Saturday = 5 (Mon=0..Sun=6)
            days_ahead = (5 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            next_saturday = today + datetime.timedelta(days=days_ahead)
            self.fields['date'].initial = next_saturday
        
    def clean(self):
        cleaned_data = super().clean()
        meet_type = cleaned_data.get('meet_type')
        participating_teams = cleaned_data.get('participating_teams')
        
        if meet_type and participating_teams:
            team_count = participating_teams.count()
            if meet_type == 'dual' and team_count != 2:
                raise forms.ValidationError({
                    'participating_teams': 'Dual meets must have exactly 2 participating teams.'
                })
            elif meet_type in ['divisional', 'invitational'] and team_count <= 2:
                raise forms.ValidationError({
                    'participating_teams': f'{meet_type.capitalize()} meets must have more than 2 participating teams.'
                })
        
        return cleaned_data


class AssignmentForm(forms.ModelForm):
    """Form for creating and updating assignments."""
    class Meta:
        model = Assignment
        fields = ['meet', 'official', 'role', 'notes', 'confirmed']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class EventFilterForm(forms.Form):
    """Form for filtering events."""
    event_number = forms.IntegerField(
        required=False, 
        label='Event Number', 
        min_value=1, 
        max_value=99,
        widget=forms.NumberInput(attrs={'placeholder': 'Filter by number'})
    )
    name = forms.CharField(
        required=False, 
        label='Event Name', 
        widget=forms.TextInput(attrs={'placeholder': 'Search by name'})
    )
    meet_type = forms.ChoiceField(
        required=False, 
        choices=[('', 'All Types')] + Event.MEET_TYPE_CHOICES, 
        label='Meet Type'
    )
    gender = forms.ChoiceField(
        required=False, 
        choices=[('', 'All Genders')] + Event.GENDER_CHOICES, 
        label='Gender'
    )


class EventForm(forms.ModelForm):
    """Form for creating and updating events."""
    class Meta:
        model = Event
        fields = ['event_number', 'name', 'description', 'meet_type', 'gender']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        event_number = cleaned_data.get('event_number')
        meet_type = cleaned_data.get('meet_type')
        
        # Check if another event exists with the same event_number and meet_type
        # but exclude the current instance if this is an update
        if event_number and meet_type:
            query = Event.objects.filter(event_number=event_number, meet_type=meet_type)
            if self.instance.pk:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                self.add_error(
                    'event_number', 
                    f'An event with number {event_number} and meet type "{dict(Event.MEET_TYPE_CHOICES).get(meet_type)}" already exists.'
                )
        
        return cleaned_data


class EventImportForm(forms.Form):
    """Form for importing events from Excel file."""
    file = forms.FileField(
        label='Select Excel file to import events',
        help_text='File must be .xlsx format with required columns: event_number, name, meet_type, gender'
    )
    replace = forms.BooleanField(
        required=False,
        label='Replace all existing events',
        help_text='Warning: This will delete all existing events before import'
    )


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['role', 'strategy', 'location', 'minimum_certification']
        widgets = {
            'role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Referee, Umpire'}),
            'strategy': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Backfield, Deep Wing'}),
            'minimum_certification': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['strategy'].queryset = Strategy.objects.all()
        self.fields['strategy'].empty_label = "Select a Strategy"
        
        # Set up the certification field with default value
        self.fields['minimum_certification'].queryset = Certification.objects.all().order_by('level', 'name')
        self.fields['minimum_certification'].empty_label = "No Minimum Certification"
        
        # If no certification is selected, try to find level 3 as default
        if not self.initial.get('minimum_certification'):
            level_3_cert = Certification.objects.filter(level=3).first()
            if level_3_cert:
                self.initial['minimum_certification'] = level_3_cert.id


class PositionImportForm(forms.Form):
    import_file = forms.FileField(
        label='Select Import File',
        help_text='Upload an Excel (.xlsx) or CSV (.csv) file containing position data. '
                  'Required columns: "Role", "Strategy Name", "Location".'
    )

    def clean_import_file(self):
        file = self.cleaned_data.get('import_file')
        if file:
            if not file.name.endswith(('.xlsx', '.csv')):
                raise forms.ValidationError('Invalid file type. Only .xlsx and .csv files are allowed.')
        return file


# Create a formset for managing pools within a team
PoolFormSet = inlineformset_factory(
    Team, 
    Pool,
    form=PoolForm,
    extra=1,  # Show one empty form by default
    can_delete=True  # Allow deleting pools
)


class EventPositionForm(forms.ModelForm):
    """Form for managing positions associated with events."""
    class Meta:
        model = EventPosition
        fields = ['position', 'is_mandatory']
        widgets = {
            'position': forms.Select(attrs={'class': 'form-select'}),
            'is_mandatory': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


# Create a formset for managing multiple event positions
EventPositionFormSet = modelformset_factory(
    EventPosition,
    form=EventPositionForm,
    extra=3,  # Show three empty forms by default
    can_delete=True
)


# Create an inline formset for managing positions within an event
EventPositionInlineFormSet = inlineformset_factory(
    Event,
    EventPosition,
    form=EventPositionForm,
    extra=3,  # Show three empty forms by default
    can_delete=True,
    fields=['position', 'is_mandatory']
)
