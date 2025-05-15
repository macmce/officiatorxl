from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .filters import DivisionFilter

# Import league and division views from this file
from .models import (Certification, League, Division, Team, 
                    Official, Meet, Assignment)
from .forms import (CertificationForm, LeagueForm, DivisionForm, TeamForm,
                   OfficialForm, MeetForm, AssignmentForm)

# Import team views
from .views_teams import (
    team_list, team_detail, team_create, team_update, team_delete,
    team_import_officials
)

# Import official and certification views
from .views_officials import (
    certification_list, certification_detail, certification_create, 
    certification_update, certification_delete,
    official_list, official_detail, official_create, 
    official_update, official_delete
)

# Import meet and assignment views
from .views_meets import (
    meet_list, meet_detail, meet_create, meet_update, meet_delete,
    assignment_list, assignment_detail, assignment_create, 
    assignment_update, assignment_delete
)

# Import template generator view
from .views_template import generate_officials_template

# Import export views
from .views_export import export_team_officials_excel, export_team_officials_json

# Import pool views
from .views_pools import pool_create, pool_update, pool_delete


@login_required
def dashboard(request):
    """Main dashboard for the officials management system."""
    user_leagues = request.user.leagues.all()
    
    # Get counts for various entities the user has access to
    division_count = Division.objects.filter(league__in=user_leagues).count()
    team_count = Team.objects.filter(division__league__in=user_leagues).count()
    official_count = Official.objects.filter(team__division__league__in=user_leagues).count()
    
    # Get upcoming meets (limited to 5)
    from django.utils import timezone
    upcoming_meets = Meet.objects.filter(
        league__in=user_leagues, 
        date__gte=timezone.now().date()
    ).order_by('date')[:5]
    
    # Get recent assignments (limited to 5)
    recent_assignments = Assignment.objects.filter(
        meet__league__in=user_leagues
    ).order_by('-assigned_at')[:5]
    
    context = {
        'user_leagues': user_leagues,
        'league_count': user_leagues.count(),
        'division_count': division_count,
        'team_count': team_count,
        'official_count': official_count,
        'upcoming_meets': upcoming_meets,
        'recent_assignments': recent_assignments,
    }
    
    return render(request, 'officials/dashboard.html', context)


# League views
@login_required
def league_list(request):
    """Display list of leagues that the user has access to."""
    user_leagues = request.user.leagues.all()
    paginator = Paginator(user_leagues, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'officials/league_list.html', {
        'page_obj': page_obj,
    })


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
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can create leagues.')
        return redirect('league_list')
    
    if request.method == 'POST':
        form = LeagueForm(request.POST, request.FILES)
        if form.is_valid():
            league = form.save()
            league.users.add(request.user)
            messages.success(request, f'League {league.name} created successfully!')
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
    
    # Only superusers can update leagues
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can edit leagues.')
        return redirect('league_list')
    
    if request.method == 'POST':
        form = LeagueForm(request.POST, request.FILES, instance=league)
        if form.is_valid():
            form.save()
            messages.success(request, f'League {league.name} updated successfully!')
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
    
    # Only superusers can delete leagues
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can delete leagues.')
        return redirect('league_list')
    
    if request.method == 'POST':
        league_name = league.name
        league.delete()
        messages.success(request, f'League {league_name} deleted successfully!')
        return redirect('league_list')
    
    return render(request, 'officials/league_confirm_delete.html', {
        'league': league,
    })


# Division views
@login_required
def division_list(request):
    """Display list of divisions that the user has access to."""
    if request.user.is_staff:
        initial_divisions_queryset = Division.objects.all().order_by('league__name', 'name')
        user_leagues = League.objects.all() # For filter consistency, though not directly used for initial queryset for staff
    else:
        user_leagues = request.user.leagues.all()
        initial_divisions_queryset = Division.objects.filter(league__in=user_leagues).order_by('league__name', 'name')

    division_filter = DivisionFilter(request.GET, queryset=initial_divisions_queryset)
    
    paginator = Paginator(division_filter.qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Force evaluation of the object_list for the current page to prevent issues with lazy QuerySets in tests
    if hasattr(page_obj, 'object_list'):
        page_obj.object_list = list(page_obj.object_list)
    
    return render(request, 'officials/division_list.html', {
        'page_obj': page_obj,
        'filter': division_filter,
    })


@login_required
def division_detail(request, pk):
    """Display details of a specific division."""
    division = get_object_or_404(Division, pk=pk)
    
    # Check if user has permission to view this division
    if not request.user.leagues.filter(id=division.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this division.')
        return redirect('division_list')
    
    teams = division.teams.all()
    
    return render(request, 'officials/division_detail.html', {
        'division': division,
        'teams': teams,
    })


@login_required
def division_create(request):
    """Create a new division."""
    # Only show leagues the user has access to
    user_leagues = request.user.leagues.all()
    
    if not user_leagues and not request.user.is_staff:
        messages.error(request, 'You do not have any leagues to add divisions to.')
        return redirect('division_list')
    
    if request.method == 'POST':
        form = DivisionForm(request.POST)
        if form.is_valid():
            division = form.save(commit=False)
            
            # Check if user has permission to add division to this league
            if not request.user.leagues.filter(id=division.league.id).exists() and not request.user.is_staff:
                messages.error(request, 'You do not have permission to add divisions to this league.')
                return redirect('division_list')
            
            division.save()
            messages.success(request, f'Division {division.name} created successfully!')
            return redirect('division_detail', pk=division.pk)
    else:
        form = DivisionForm()
        # Limit league choices to those the user has access to
        if not request.user.is_staff:
            form.fields['league'].queryset = user_leagues
    
    return render(request, 'officials/division_form.html', {
        'form': form,
        'title': 'Create Division',
    })


@login_required
def division_update(request, pk):
    """Update an existing division."""
    division = get_object_or_404(Division, pk=pk)
    
    # Check if user has permission to edit this division
    if not request.user.leagues.filter(id=division.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this division.')
        return redirect('division_list')
    
    if request.method == 'POST':
        form = DivisionForm(request.POST, instance=division)
        if form.is_valid():
            form.save()
            messages.success(request, f'Division {division.name} updated successfully!')
            return redirect('division_detail', pk=division.pk)
    else:
        form = DivisionForm(instance=division)
        # Limit league choices to those the user has access to if not staff
        if not request.user.is_staff:
            form.fields['league'].queryset = request.user.leagues.all()
    
    return render(request, 'officials/division_form.html', {
        'form': form,
        'title': 'Update Division',
        'division': division,
    })


@login_required
def division_delete(request, pk):
    """Delete an existing division."""
    division = get_object_or_404(Division, pk=pk)
    
    # Check if user has permission to delete this division
    if not request.user.leagues.filter(id=division.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this division.')
        return redirect('division_list')
    
    if request.method == 'POST':
        division_name = division.name
        division.delete()
        messages.success(request, f'Division {division_name} deleted successfully!')
        return redirect('division_list')
    
    return render(request, 'officials/division_confirm_delete.html', {
        'division': division,
    })
