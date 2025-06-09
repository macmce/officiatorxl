from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from officials.models import League, UserLeagueAdmin


class SignUpView(CreateView):
    """View for user registration."""
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/signup.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! You can now log in.')
        return response


@login_required
def dashboard(request):
    """Dashboard view for authenticated users."""
    user_leagues = request.user.leagues.all()
    context = {
        'user_leagues': user_leagues,
    }
    return render(request, 'users/dashboard.html', context)


# Profile view removed as it was redundant with user_update


def logout_view(request):
    """Custom logout view to ensure proper redirection."""
    logout(request)
    messages.success(request, 'You have been successfully logged out!')
    return redirect('login')
