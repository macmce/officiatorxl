from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Pool, Team
from .forms import PoolForm


@login_required
def pool_create(request, team_id):
    """Create a new pool for a specific team."""
    team = get_object_or_404(Team, pk=team_id)
    
    # Check if user has permission to add pools to this team
    if not request.user.leagues.filter(id=team.division.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to add pools to this team.')
        return redirect('team_detail', pk=team_id)
    
    if request.method == 'POST':
        form = PoolForm(request.POST)
        if form.is_valid():
            pool = form.save(commit=False)
            pool.team = team
            pool.save()
            messages.success(request, f'Pool {pool.name} added successfully!')
            return redirect('team_detail', pk=team_id)
    else:
        form = PoolForm(initial={'team': team})
        # Hide the team field as it's pre-selected
        form.fields['team'].widget = form.fields['team'].hidden_widget()
        form.fields['team'].initial = team
    
    return render(request, 'officials/pool_form.html', {
        'form': form,
        'title': f'Add Pool for {team.name}',
        'team': team,
    })


@login_required
def pool_update(request, pk):
    """Update an existing pool."""
    pool = get_object_or_404(Pool, pk=pk)
    team = pool.team
    
    # Check if user has permission to edit this pool
    if not request.user.leagues.filter(id=team.division.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this pool.')
        return redirect('team_detail', pk=team.id)
    
    if request.method == 'POST':
        form = PoolForm(request.POST, instance=pool)
        if form.is_valid():
            form.save()
            messages.success(request, f'Pool {pool.name} updated successfully!')
            return redirect('team_detail', pk=team.id)
    else:
        form = PoolForm(instance=pool)
        # Limit team choices to the current team
        form.fields['team'].queryset = Team.objects.filter(id=team.id)
    
    return render(request, 'officials/pool_form.html', {
        'form': form,
        'title': f'Update Pool: {pool.name}',
        'pool': pool,
        'team': team,
    })


@login_required
def pool_delete(request, pk):
    """Delete an existing pool."""
    pool = get_object_or_404(Pool, pk=pk)
    team = pool.team
    
    # Check if user has permission to delete this pool
    if not request.user.leagues.filter(id=team.division.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this pool.')
        return redirect('team_detail', pk=team.id)
    
    if request.method == 'POST':
        pool_name = pool.name
        pool.delete()
        messages.success(request, f'Pool {pool_name} deleted successfully!')
        return redirect('team_detail', pk=team.id)
    
    return render(request, 'officials/pool_confirm_delete.html', {
        'pool': pool,
        'team': team,
    })
