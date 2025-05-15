from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group
from .models import CustomUser


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
    """Form for admins to edit user details."""
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 
                 'profile_image', 'is_active', 'is_staff')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class UserRoleForm(forms.ModelForm):
    """Form for managing user roles and permissions."""
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Select the groups this user belongs to'
    )
    
    is_staff = forms.BooleanField(
        required=False,
        help_text='Designates whether the user can log into the admin site'
    )
    
    is_superuser = forms.BooleanField(
        required=False,
        help_text='Designates that this user has all permissions without explicitly assigning them'
    )
    
    class Meta:
        model = CustomUser
        fields = ('is_active', 'is_staff', 'is_superuser', 'groups')
