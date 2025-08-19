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
        fields = ['league', 'division', 'date', 'start_time', 'host_team', 'pool', 'name', 'meet_type', 'strategy', 'participating_teams']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'meet_type': forms.Select(),
            'name': forms.TextInput(attrs={'placeholder': 'Enter meet name'}),
            'pool': PoolSelectWidget(),
            'strategy': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add a hidden field to track whether name field is auto-generated
        self.auto_generated_name = True
        
        # Make name field required
        self.fields['name'].required = True

        # Strategy field setup (optional for tests; model allows null/blank)
        self.fields['strategy'].queryset = Strategy.objects.all()
        self.fields['strategy'].required = False
        # Do not allow an empty selection in the dropdown
        try:
            self.fields['strategy'].empty_label = None
        except Exception:
            pass
        
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
        # Allow omission of start_time; model has a default
        self.fields['start_time'].required = False
        
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
    # Extra fields for create flow
    new_official_name = forms.CharField(
        required=False,
        label='New Official Name',
        widget=forms.TextInput(attrs={'placeholder': 'Enter new official name'})
    )
    new_official_email = forms.EmailField(
        required=False,
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'name@example.com'})
    )
    new_official_phone = forms.CharField(
        required=False,
        label='Phone',
        widget=forms.TextInput(attrs={'placeholder': 'e.g., (555) 555-5555'})
    )
    new_official_team = forms.ModelChoiceField(
        queryset=Team.objects.none(),
        required=False,
        label='Team',
        widget=forms.Select()
    )
    new_official_active = forms.BooleanField(
        required=False,
        initial=True,
        label='Active'
    )
    new_official_proficiency = forms.ChoiceField(
        choices=Official.PROFICIENCY_CHOICES,
        required=False,
        label='Proficiency'
    )
    new_official_certification = forms.ModelChoiceField(
        queryset=Certification.objects.all().order_by('level', 'name'),
        required=False,
        label='Certification'
    )
    class Meta:
        model = Assignment
        fields = ['meet', 'official', 'role', 'notes', 'confirmed']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # When updating, do not allow changing confirmed, meet, or official
        if self.instance and self.instance.pk:
            # Add a proficiency selector for the assigned official (update only)
            try:
                current_prof = getattr(self.instance.official, 'proficiency', None)
            except Exception:
                current_prof = None
            self.fields['official_proficiency'] = forms.ChoiceField(
                choices=Official.PROFICIENCY_CHOICES,
                required=False,
                label='Proficiency',
                initial=current_prof,
                widget=forms.Select()
            )
            for fname in ['meet', 'official', 'confirmed']:
                if fname in self.fields:
                    self.fields[fname].disabled = True
        else:
            # Creating: if an official is present, default role to their certification
            official_id = None
            try:
                official_id = self.initial.get('official') or self.data.get('official')
            except Exception:
                official_id = None
            if official_id:
                try:
                    official_obj = Official.objects.get(pk=official_id)
                    if official_obj.certification and 'role' in self.fields:
                        # Pre-fill role text with certification name
                        self.initial['role'] = official_obj.certification.name
                except (Official.DoesNotExist, ValueError, TypeError):
                    pass
            # Create screen: make meet and confirmed read-only as well
            for fname in ['meet', 'confirmed']:
                if fname in self.fields:
                    self.fields[fname].disabled = True
            # Allow create to omit 'official' if providing a new name
            if 'official' in self.fields:
                self.fields['official'].required = False
            # Role will only be required if selecting an existing official
            if 'role' in self.fields:
                self.fields['role'].required = False

    def clean_role(self):
        """Validate role as plain text. When creating a new official, allow empty."""
        role_val = self.cleaned_data.get('role', '')
        instance_exists = bool(getattr(self.instance, 'pk', None))
        new_name = (self.data.get('new_official_name') or '').strip()
        official_id = self.data.get('official')
        # If updating, or if an existing official is selected, require non-empty role string
        if instance_exists or (official_id and not new_name):
            if not role_val:
                raise ValidationError('Please enter a certification/role.')
            return role_val
        # New-official path: role may be empty; will be inferred from new_official_certification in the view
        return role_val or ''

    def clean(self):
        cleaned = super().clean()
        # On create, either an existing official or a new name must be provided
        instance_exists = bool(getattr(self.instance, 'pk', None))
        if not instance_exists:
            official = cleaned.get('official')
            new_name = (cleaned.get('new_official_name') or '').strip()
            if official and new_name:
                raise ValidationError('Please either select an existing official or enter a new official, not both.')
            if not official and not new_name:
                raise ValidationError('Select an existing official or enter a new official name.')
            if not official and new_name:
                # Require full new-official details
                # Team is mandatory for Official model
                if not cleaned.get('new_official_team'):
                    self.add_error('new_official_team', 'Team is required for a new official.')
                if not cleaned.get('new_official_certification'):
                    self.add_error('new_official_certification', 'Certification is required for a new official.')
                # Proficiency optional defaults handled in view if omitted
                # Email/phone optional
                # Active defaults to True if omitted
            if official and not new_name:
                # Existing official path requires role (certification)
                if not cleaned.get('role'):
                    self.add_error('role', 'Certification is required when selecting an existing official.')
        return cleaned


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
