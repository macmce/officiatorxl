from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm, AdminUserEditForm, UserRoleForm, RoleRequiredUserCreationForm
from officials.models import League, Team, UserLeagueAdmin

def is_admin(user):
    """Check if user is an admin or staff member."""
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def user_list(request):
    """View for listing all users (admin only)."""
    search_query = request.GET.get('search', '')
    
    if search_query:
        users = CustomUser.objects.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        ).order_by('username')
    else:
        users = CustomUser.objects.all().order_by('username')
    
    paginator = Paginator(users, 15)  # Show 15 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/admin/user_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
    })

# user_detail view has been removed as it was redundant with user_update

@login_required
@user_passes_test(is_admin)
def user_create(request):
    """View for creating a new user (admin only)."""
    if request.method == 'POST':
        form = RoleRequiredUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'User {user.username} created successfully with assigned roles!')
                return redirect('user_update', pk=user.pk)
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
        else:
            # Add specific error messages for form validation failures
            if form.errors:
                messages.error(request, 'Please correct the errors below to create the user.')
    else:
        form = RoleRequiredUserCreationForm()
    
    return render(request, 'users/admin/user_form.html', {
        'form': form,
        'title': 'Create User',
    })

@login_required
@user_passes_test(is_admin)
def user_update(request, pk):
    """View for updating an existing user (admin only)."""
    user = get_object_or_404(CustomUser, pk=pk)
    user_leagues = user.leagues.all()
    
    # Get the leagues where the user is an admin
    admin_league_ids = UserLeagueAdmin.objects.filter(user=user).values_list('league_id', flat=True)
    
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save()
            
            # Handle league associations
            selected_leagues = form.cleaned_data.get('leagues')
            if selected_leagues:
                user.leagues.set(selected_leagues)
            
            # Handle team associations
            selected_teams = form.cleaned_data.get('teams')
            if selected_teams:
                user.teams.set(selected_teams)
            else:
                user.teams.clear()
            
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('user_update', pk=user.pk)
    else:
        form = AdminUserEditForm(instance=user)
    
    return render(request, 'users/admin/user_form.html', {
        'form': form,
        'title': 'Update User',
        'user_obj': user,
        'user_leagues': user_leagues,
        'admin_league_ids': admin_league_ids,
    })

@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    """View for deleting a user (admin only)."""
    user = get_object_or_404(CustomUser, pk=pk)
    
    # Prevent self-deletion
    if user == request.user:
        messages.error(request, 'You cannot delete your own account!')
        return redirect('user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('user_list')
    
    return render(request, 'users/admin/user_confirm_delete.html', {
        'user_obj': user,
    })

@login_required
@user_passes_test(is_admin)
def user_roles(request, pk):
    """View for managing user roles and permissions (admin only)."""
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Roles for {user.username} updated successfully!')
            return redirect('user_update', pk=user.pk)
    else:
        form = UserRoleForm(instance=user)
    
    return render(request, 'users/admin/user_roles.html', {
        'form': form,
        'user_obj': user,
    })

@login_required
@user_passes_test(is_admin)
def user_leagues(request, pk):
    """View for managing user league associations and admin status (admin only)."""
    user = get_object_or_404(CustomUser, pk=pk)
    leagues = League.objects.all().order_by('name')
    
    # Get the leagues where the user is an admin
    admin_league_ids = UserLeagueAdmin.objects.filter(user=user).values_list('league_id', flat=True)
    
    if request.method == 'POST':
        # Get selected league IDs from the form
        selected_league_ids = request.POST.getlist('leagues')
        # Get league IDs where the user should be an admin
        admin_for_leagues = request.POST.getlist('league_admin')
        
        # Clear current league associations and add new ones
        user.leagues.clear()
        if selected_league_ids:
            selected_leagues = League.objects.filter(id__in=selected_league_ids)
            user.leagues.add(*selected_leagues)
        
        # Clear all existing admin roles first
        UserLeagueAdmin.objects.filter(user=user).delete()
        
        # Add admin roles for selected leagues
        if admin_for_leagues:
            for league_id in admin_for_leagues:
                # Only create admin entries for leagues that the user is associated with
                if league_id in selected_league_ids:
                    UserLeagueAdmin.objects.create(
                        user=user,
                        league_id=league_id
                    )
        
        messages.success(request, f'League associations and admin roles for {user.username} updated successfully!')
        return redirect('user_update', pk=user.pk)
    
    user_league_ids = user.leagues.values_list('id', flat=True)
    
    return render(request, 'users/admin/user_leagues.html', {
        'user_obj': user,
        'leagues': leagues,
        'user_league_ids': user_league_ids,
        'admin_league_ids': admin_league_ids,
    })


@login_required
@user_passes_test(is_admin)
def user_teams(request, pk):
    """View for managing user team associations (admin only)."""
    user = get_object_or_404(CustomUser, pk=pk)
    
    # Get leagues the user is associated with
    user_leagues = user.leagues.all()
    
    # Get teams from those leagues
    available_teams = Team.objects.filter(division__league__in=user_leagues).order_by('name')
    
    if request.method == 'POST':
        # Get selected team IDs from the form
        selected_team_ids = request.POST.getlist('teams')
        
        # Clear current team associations and add new ones
        user.teams.clear()
        if selected_team_ids:
            selected_teams = Team.objects.filter(id__in=selected_team_ids)
            user.teams.add(*selected_teams)
        
        messages.success(request, f'Team associations for {user.username} updated successfully!')
        return redirect('user_update', pk=user.pk)
    
    user_team_ids = user.teams.values_list('id', flat=True)
    
    # Group teams by league for easier selection
    league_teams = {}
    for league in user_leagues:
        league_teams[league] = available_teams.filter(division__league=league)
    
    return render(request, 'users/admin/user_teams.html', {
        'user_obj': user,
        'league_teams': league_teams,
        'user_team_ids': user_team_ids,
    })
