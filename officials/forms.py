from django import forms
from .models import Certification, League, Division, Team, Pool, Official, Meet, Assignment, Event, Position, Strategy


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


class MeetForm(forms.ModelForm):
    """Form for creating and updating meets."""
    class Meta:
        model = Meet
        fields = ['league', 'date', 'host_team', 'pool', 'name', 'meet_type', 'participating_teams']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'meet_type': forms.Select(),
        }


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
        fields = ['role', 'strategy', 'location']
        widgets = {
            'role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Referee, Umpire'}),
            'strategy': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Backfield, Deep Wing'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['strategy'].queryset = Strategy.objects.all()
        self.fields['strategy'].empty_label = "Select a Strategy"


class PositionImportForm(forms.Form):
    import_file = forms.FileField(
        label='Select Import File',
        help_text='Upload an Excel (.xlsx) or CSV (.csv) file containing position data. '
                  'Required columns: "Role", "Strategy Name", "Location" (optional).'
    )
    update_existing = forms.BooleanField(
        label='Update existing positions',
        required=False,
        initial=True,
        help_text='If checked, positions with the same Role and Strategy Name will be updated. '
                  'Otherwise, they will be skipped if they already exist.'
    )

    def clean_import_file(self):
        file = self.cleaned_data.get('import_file')
        if file:
            if not file.name.endswith(('.xlsx', '.csv')):
                raise forms.ValidationError('Invalid file type. Only .xlsx and .csv files are allowed.')
        return file
