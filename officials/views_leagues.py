from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import League, Division
from .forms import LeagueForm, DivisionForm
from .filters import LeagueFilter

class LeagueListView(LoginRequiredMixin, FilterView):
    """
    Display list of leagues that the user has access to with filtering capability.
    """
    model = League
    filterset_class = LeagueFilter
    template_name = 'officials/league_list.html'
    context_object_name = 'leagues'
    paginate_by = 10
    
    def get_queryset(self):
        """Filter leagues to only show those the user has access to."""
        return self.request.user.leagues.all().order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if any filters are active
        context['filters_active'] = any(self.request.GET.get(param) for param in self.request.GET if param != 'page')
        return context

@login_required
def league_detail(request, pk):
    """Display details of a specific league."""
    league = get_object_or_404(League, pk=pk)

    # Check if user has permission to view this league
    if not request.user.leagues.filter(id=pk).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this league.')
        return redirect('league_list')
    
    divisions = league.divisions.all()
    
    return render(request, 'officials/league_detail.html', {
        'league': league,
        'divisions': divisions,
    })

@login_required
def league_create(request):
    """Create a new league."""
    if request.method == 'POST':
        form = LeagueForm(request.POST, request.FILES)
        if form.is_valid():
            league = form.save()
            # Add the current user to the league's users
            league.users.add(request.user)
            messages.success(request, 'League created successfully.')
            return redirect('league_detail', pk=league.pk)
    else:
        form = LeagueForm()
    
    return render(request, 'officials/league_form.html', {
        'form': form,
        'title': 'Create League',
    })

@login_required
def league_update(request, pk):
    """Update an existing league."""
    league = get_object_or_404(League, pk=pk)
    
    # Check if user has permission to update this league
    if not request.user.leagues.filter(id=pk).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to update this league.')
        return redirect('league_list')
    
    if request.method == 'POST':
        form = LeagueForm(request.POST, request.FILES, instance=league)
        if form.is_valid():
            form.save()
            messages.success(request, 'League updated successfully.')
            return redirect('league_detail', pk=league.pk)
    else:
        form = LeagueForm(instance=league)
    
    return render(request, 'officials/league_form.html', {
        'form': form,
        'title': 'Update League',
        'league': league,
    })

@login_required
def league_delete(request, pk):
    """Delete an existing league."""
    league = get_object_or_404(League, pk=pk)
    
    # Check if user has permission to delete this league
    if not request.user.leagues.filter(id=pk).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this league.')
        return redirect('league_list')
    
    if request.method == 'POST':
        league.delete()
        messages.success(request, 'League deleted successfully.')
        return redirect('league_list')
    
    return render(request, 'officials/league_confirm_delete.html', {
        'league': league,
    })
