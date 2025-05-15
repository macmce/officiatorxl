from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Official, Team, Certification
from .forms import OfficialForm, CertificationForm


# Certification views
@login_required
def certification_list(request):
    """Display list of certifications."""
    certifications = Certification.objects.all().order_by('level', 'name')
    
    paginator = Paginator(certifications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'officials/certification_list.html', {
        'page_obj': page_obj,
    })


@login_required
def certification_detail(request, pk):
    """Display details of a specific certification."""
    certification = get_object_or_404(Certification, pk=pk)
    officials = certification.officials.all()
    
    return render(request, 'officials/certification_detail.html', {
        'certification': certification,
        'officials': officials,
    })


@login_required
def certification_create(request):
    """Create a new certification."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to create certifications.')
        return redirect('certification_list')
    
    if request.method == 'POST':
        form = CertificationForm(request.POST)
        if form.is_valid():
            certification = form.save()
            messages.success(request, f'Certification {certification.name} created successfully!')
            return redirect('certification_detail', pk=certification.pk)
    else:
        form = CertificationForm()
    
    return render(request, 'officials/certification_form.html', {
        'form': form,
        'title': 'Create Certification',
    })


@login_required
def certification_update(request, pk):
    """Update an existing certification."""
    certification = get_object_or_404(Certification, pk=pk)
    
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to update certifications.')
        return redirect('certification_list')
    
    if request.method == 'POST':
        form = CertificationForm(request.POST, instance=certification)
        if form.is_valid():
            form.save()
            messages.success(request, f'Certification {certification.name} updated successfully!')
            return redirect('certification_detail', pk=certification.pk)
    else:
        form = CertificationForm(instance=certification)
    
    return render(request, 'officials/certification_form.html', {
        'form': form,
        'title': 'Update Certification',
        'certification': certification,
    })


@login_required
def certification_delete(request, pk):
    """Delete an existing certification."""
    certification = get_object_or_404(Certification, pk=pk)
    
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete certifications.')
        return redirect('certification_list')
    
    if request.method == 'POST':
        certification_name = certification.name
        certification.delete()
        messages.success(request, f'Certification {certification_name} deleted successfully!')
        return redirect('certification_list')
    
    return render(request, 'officials/certification_confirm_delete.html', {
        'certification': certification,
    })


# Official views
@login_required
def official_list(request):
    """Display list of officials that the user has access to."""
    user_leagues = request.user.leagues.all()
    officials = Official.objects.filter(team__division__league__in=user_leagues).order_by('name')
    
    paginator = Paginator(officials, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'officials/official_list.html', {
        'page_obj': page_obj,
    })


@login_required
def official_detail(request, pk):
    """Display details of a specific official."""
    official = get_object_or_404(Official, pk=pk)
    
    # Check if user has permission to view this official by checking if they share at least one league
    user_leagues = request.user.leagues.all()
    official_league = official.team.division.league if official.team else None
    
    if official_league not in user_leagues and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this official.')
        return redirect('official_list')
    
    assignments = official.assignments.all().order_by('-meet__date')
    
    return render(request, 'officials/official_detail.html', {
        'official': official,

        'assignments': assignments,
    })


@login_required
def official_create(request):
    """Create a new official."""
    # Get teams from leagues the user has access to
    user_leagues = request.user.leagues.all()
    accessible_teams = Team.objects.filter(division__league__in=user_leagues)
    
    if request.method == 'POST':
        form = OfficialForm(request.POST)
        if form.is_valid():
            official = form.save()
            messages.success(request, f'Official {official.name} created successfully!')
            return redirect('official_detail', pk=official.pk)
    else:
        form = OfficialForm()
        # Limit team choices to those the user has access to
        if not request.user.is_staff:
            form.fields['team'].queryset = accessible_teams
    
    return render(request, 'officials/official_form.html', {
        'form': form,
        'title': 'Create Official',
    })


@login_required
def official_update(request, pk):
    """Update an existing official."""
    official = get_object_or_404(Official, pk=pk)
    
    # Check if user has permission to edit this official
    user_leagues = request.user.leagues.all()
    official_league = official.team.division.league if official.team else None
    
    if official_league not in user_leagues and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this official.')
        return redirect('official_list')
    
    if request.method == 'POST':
        form = OfficialForm(request.POST, instance=official)
        if form.is_valid():
            form.save()
            messages.success(request, f'Official {official.name} updated successfully!')
            return redirect('official_detail', pk=official.pk)
    else:
        form = OfficialForm(instance=official)
        # Limit team choices to those the user has access to if not staff
        if not request.user.is_staff:
            accessible_teams = Team.objects.filter(division__league__in=user_leagues)
            form.fields['team'].queryset = accessible_teams
    
    return render(request, 'officials/official_form.html', {
        'form': form,
        'title': 'Update Official',
        'official': official,
    })


@login_required
def official_delete(request, pk):
    """Delete an existing official."""
    official = get_object_or_404(Official, pk=pk)
    
    # Check if user has permission to delete this official
    user_leagues = request.user.leagues.all()
    official_league = official.team.division.league if official.team else None
    
    if official_league not in user_leagues and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this official.')
        return redirect('official_list')
    
    if request.method == 'POST':
        official_name = official.name
        official.delete()
        messages.success(request, f'Official {official_name} deleted successfully!')
        return redirect('official_list')
    
    return render(request, 'officials/official_confirm_delete.html', {
        'official': official,
    })
