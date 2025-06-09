from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group
from .models import CustomUser
from officials.models import League, Team


class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users."""
    # Add email and name fields explicitly as UserCreationForm doesn't include them by default
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """Form for updating users."""
    password = None  # Hide the password field
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'profile_image')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class AdminUserEditForm(forms.ModelForm):
    """Form for admins to edit user details, including league and team associations."""
    
    def add_warning(self, field, message):
        """Add a non-error message that will be displayed with the field."""
        if not hasattr(self, '_warnings'):
            self._warnings = {}
        if field not in self._warnings:
            self._warnings[field] = []
        self._warnings[field].append(message)
    
    leagues = forms.ModelMultipleChoiceField(
        queryset=League.objects.all().order_by('name'),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        help_text='User must be associated with at least one league'
    )
    
    teams = forms.ModelMultipleChoiceField(
        queryset=Team.objects.all().order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Optionally associate user with specific teams'
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 
                 'profile_image', 'is_active', 'is_staff', 'is_superuser')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize leagues and teams if instance exists
        if self.instance.pk:
            self.initial['leagues'] = self.instance.leagues.all()
            self.initial['teams'] = self.instance.teams.all()
            
        # Rename staff field to League Admin
        self.fields['is_staff'].label = 'League Admin'
            
    def clean_leagues(self):
        """Validate that at least one league is selected."""
        leagues = self.cleaned_data.get('leagues')
        if not leagues or len(leagues) == 0:
            raise forms.ValidationError("You must associate the user with at least one league.")
        return leagues
        
    def clean(self):
        """Additional cross-field validation."""
        cleaned_data = super().clean()
        leagues = cleaned_data.get('leagues')
        teams = cleaned_data.get('teams')
        is_staff = cleaned_data.get('is_staff')
        is_superuser = cleaned_data.get('is_superuser')
        
        # If user is a superuser, they should also be staff
        if is_superuser and not is_staff:
            cleaned_data['is_staff'] = True
            self.add_warning('is_staff', 'League Admin status was automatically enabled because the user is a superuser.')
        
        # If teams are selected, verify they're from selected leagues
        if leagues and teams:
            league_ids = [league.id for league in leagues]
            # Get teams that belong to divisions of the selected leagues
            for team in teams:
                if team.division.league.id not in league_ids:
                    self.add_error('teams', 
                        f"Team '{team.name}' belongs to league '{team.division.league.name}' "
                        f"which is not in your selected leagues. Please select the league first.")
            
        return cleaned_data


class UserRoleForm(forms.ModelForm):
    """Form for managing user roles and permissions."""
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Select the groups this user belongs to'
    )
    
    is_staff = forms.BooleanField(
        label="League Admin",
        required=False,
        help_text='Designates whether the user can manage leagues and their settings'
    )
    
    is_superuser = forms.BooleanField(
        required=False,
        help_text='Designates that this user has all permissions without explicitly assigning them'
    )
    
    class Meta:
        model = CustomUser
        fields = ('is_active', 'is_staff', 'is_superuser', 'groups')


class RoleRequiredUserCreationForm(UserCreationForm):
    """Form for creating new users with required role specification and league associations."""
    # Add email and name fields explicitly as UserCreationForm doesn't include them by default
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    
    # Add role fields
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,  # Groups are optional
        widget=forms.CheckboxSelectMultiple,
        help_text='Optionally select groups for this user'
    )
    
    # Add league and team fields
    leagues = forms.ModelMultipleChoiceField(
        queryset=League.objects.all().order_by('name'),
        required=True,  # Leagues are required
        widget=forms.CheckboxSelectMultiple,
        help_text='User must be associated with at least one league'
    )
    
    teams = forms.ModelMultipleChoiceField(
        queryset=Team.objects.all().order_by('name'),
        required=False,  # Teams are optional
        widget=forms.CheckboxSelectMultiple,
        help_text='Optionally associate user with specific teams'
    )
    
    is_active = forms.BooleanField(
        required=False, 
        initial=True,
        help_text='Designates whether this user account should be considered active'
    )
    
    is_staff = forms.BooleanField(
        required=False,
        help_text='Designates whether the user can manage leagues and their settings'
    )
    
    is_superuser = forms.BooleanField(
        required=False,
        help_text='Designates that this user has all permissions without explicitly assigning them'
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 
                 'is_active', 'is_staff', 'is_superuser', 'groups', 'leagues', 'teams')
    
    def clean_groups(self):
        """Process the groups field."""
        groups = self.cleaned_data.get('groups')
        return groups
        
    def clean_leagues(self):
        """Validate that at least one league is selected."""
        leagues = self.cleaned_data.get('leagues')
        if not leagues or len(leagues) == 0:
            raise forms.ValidationError("You must associate the user with at least one league.")
        return leagues
    
    def clean(self):
        """Additional cross-field validation."""
        cleaned_data = super().clean()
        is_staff = cleaned_data.get('is_staff')
        is_superuser = cleaned_data.get('is_superuser')
        
        # If user is a superuser, they should also be staff
        if is_superuser and not is_staff:
            cleaned_data['is_staff'] = True
            self.add_warning('is_staff', 'League Admin status was automatically enabled because the user is a superuser.')
        
        # If teams are selected, verify they're from selected leagues
        leagues = cleaned_data.get('leagues')
        teams = cleaned_data.get('teams')
        
        if leagues and teams:
            league_ids = [league.id for league in leagues]
            # Get teams that belong to divisions of the selected leagues
            for team in teams:
                if team.division.league.id not in league_ids:
                    self.add_error('teams', 
                        f"Team '{team.name}' belongs to league '{team.division.league.name}' "
                        f"which is not in your selected leagues. Please select the league first.")
            
        return cleaned_data
    
    def add_warning(self, field, message):
        """Add a non-error message that will be displayed with the field."""
        if not hasattr(self, '_warnings'):
            self._warnings = {}
        if field not in self._warnings:
            self._warnings[field] = []
        self._warnings[field].append(message)
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = self.cleaned_data.get('is_active', True)
        user.is_staff = self.cleaned_data['is_staff']
        user.is_superuser = self.cleaned_data['is_superuser']
        
        if commit:
            user.save()
            # Add selected groups
            self.save_m2m()
            
            # Additional manual associations for leagues and teams
            # (not handled by save_m2m since they're not part of the User model directly)
            leagues = self.cleaned_data.get('leagues')
            if leagues:
                user.leagues.set(leagues)
                
            teams = self.cleaned_data.get('teams')
            if teams:
                user.teams.set(teams)
            
        return user
