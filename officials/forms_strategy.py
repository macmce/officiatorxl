from django import forms
from .models import Strategy

class StrategyForm(forms.ModelForm):
    """Form for creating and updating strategies."""
    class Meta:
        model = Strategy
        fields = ['name']
        widgets = {
            'name': forms.Select(choices=Strategy.STRATEGY_CHOICES),
        }
