from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Meet, Assignment, Team, Official, League
from .forms import MeetForm, AssignmentForm


# Meet views
@login_required
def meet_list(request):
    """Display list of meets that the user has access to."""
    user_leagues = request.user.leagues.all()
    meets = Meet.objects.filter(league__in=user_leagues).order_by('-date')
    
    paginator = Paginator(meets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'officials/meet_list.html', {
        'page_obj': page_obj,
    })


@login_required
def meet_detail(request, pk):
    """Display details of a specific meet."""
    meet = get_object_or_404(Meet, pk=pk)
    
    # Check if user has permission to view this meet
    if not request.user.leagues.filter(id=meet.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this meet.')
        return redirect('meet_list')
    
    assignments = meet.assignments.all().select_related('official')
    participating_teams = meet.participating_teams.all()
    
    return render(request, 'officials/meet_detail.html', {
        'meet': meet,
        'assignments': assignments,
        'participating_teams': participating_teams,
    })


@login_required
def meet_create(request):
    """Create a new meet."""
    # Only show leagues the user has access to
    user_leagues = request.user.leagues.all()
    
    if not user_leagues and not request.user.is_staff:
        messages.error(request, 'You do not have any leagues to add meets to.')
        return redirect('meet_list')
    
    if request.method == 'POST':
        form = MeetForm(request.POST)
        if form.is_valid():
            meet = form.save(commit=False)
            
            # Check if user has permission to add meet to this league
            if not request.user.leagues.filter(id=meet.league.id).exists() and not request.user.is_staff:
                messages.error(request, 'You do not have permission to add meets to this league.')
                return redirect('meet_list')
            
            meet.save()
            # Save many-to-many relationships
            form.save_m2m()
            messages.success(request, f'Meet {meet.name} created successfully!')
            return redirect('meet_detail', pk=meet.pk)
    else:
        form = MeetForm()
        # Limit league and team choices to those the user has access to
        if not request.user.is_staff:
            form.fields['league'].queryset = user_leagues
            accessible_teams = Team.objects.filter(division__league__in=user_leagues)
            form.fields['host_team'].queryset = accessible_teams
            form.fields['participating_teams'].queryset = accessible_teams
    
    return render(request, 'officials/meet_form.html', {
        'form': form,
        'title': 'Create Meet',
    })


@login_required
def meet_update(request, pk):
    """Update an existing meet."""
    meet = get_object_or_404(Meet, pk=pk)
    
    # Check if user has permission to edit this meet
    if not request.user.leagues.filter(id=meet.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this meet.')
        return redirect('meet_list')
    
    if request.method == 'POST':
        form = MeetForm(request.POST, instance=meet)
        if form.is_valid():
            form.save()
            messages.success(request, f'Meet {meet.name} updated successfully!')
            return redirect('meet_detail', pk=meet.pk)
    else:
        form = MeetForm(instance=meet)
        # Limit league and team choices to those the user has access to if not staff
        if not request.user.is_staff:
            user_leagues = request.user.leagues.all()
            form.fields['league'].queryset = user_leagues
            accessible_teams = Team.objects.filter(division__league__in=user_leagues)
            form.fields['host_team'].queryset = accessible_teams
            form.fields['participating_teams'].queryset = accessible_teams
    
    return render(request, 'officials/meet_form.html', {
        'form': form,
        'title': 'Update Meet',
        'meet': meet,
    })


@login_required
def meet_delete(request, pk):
    """Delete an existing meet."""
    meet = get_object_or_404(Meet, pk=pk)
    
    # Check if user has permission to delete this meet
    if not request.user.leagues.filter(id=meet.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this meet.')
        return redirect('meet_list')
    
    if request.method == 'POST':
        meet_name = meet.name
        meet.delete()
        messages.success(request, f'Meet {meet_name} deleted successfully!')
        return redirect('meet_list')
    
    return render(request, 'officials/meet_confirm_delete.html', {
        'meet': meet,
    })


# Assignment views
@login_required
def assignment_list(request):
    """Display list of assignments that the user has access to."""
    user_leagues = request.user.leagues.all()
    assignments = Assignment.objects.filter(meet__league__in=user_leagues).order_by('-meet__date')
    
    paginator = Paginator(assignments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'officials/assignment_list.html', {
        'page_obj': page_obj,
    })


@login_required
def assignment_detail(request, pk):
    """Display details of a specific assignment."""
    assignment = get_object_or_404(Assignment, pk=pk)
    
    # Check if user has permission to view this assignment
    if not request.user.leagues.filter(id=assignment.meet.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this assignment.')
        return redirect('assignment_list')
    
    return render(request, 'officials/assignment_detail.html', {
        'assignment': assignment,
    })


@login_required
def assignment_create(request, meet_id=None):
    """Create a new assignment."""
    # Get meets and officials from leagues the user has access to
    user_leagues = request.user.leagues.all()
    
    if not user_leagues and not request.user.is_staff:
        messages.error(request, 'You do not have any leagues to add assignments to.')
        return redirect('assignment_list')
    
    # Pre-select meet if coming from meet detail page
    initial_data = {}
    if meet_id:
        meet = get_object_or_404(Meet, pk=meet_id)
        if request.user.leagues.filter(id=meet.league.id).exists() or request.user.is_staff:
            initial_data['meet'] = meet
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            
            # Check if user has permission to add assignment to this meet
            if not request.user.leagues.filter(id=assignment.meet.league.id).exists() and not request.user.is_staff:
                messages.error(request, 'You do not have permission to add assignments to this meet.')
                return redirect('assignment_list')
            
            # Check if this official has the necessary certification
            if assignment.official.certification is None:
                messages.warning(request, f'Note: {assignment.official.name} has no certification.')
            
            try:
                assignment.save()
                messages.success(request, f'Assignment for {assignment.official.name} created successfully!')
                return redirect('meet_detail', pk=assignment.meet.pk)
            except Exception as e:
                messages.error(request, f'Error creating assignment: {str(e)}')
    else:
        form = AssignmentForm(initial=initial_data)
        # Limit meet and official choices to those the user has access to
        if not request.user.is_staff:
            accessible_meets = Meet.objects.filter(league__in=user_leagues)
            form.fields['meet'].queryset = accessible_meets
            
            # Get officials that belong to teams in the user's leagues
            accessible_officials = Official.objects.filter(team__division__league__in=user_leagues)
            form.fields['official'].queryset = accessible_officials
    
    return render(request, 'officials/assignment_form.html', {
        'form': form,
        'title': 'Create Assignment',
    })


@login_required
def assignment_update(request, pk):
    """Update an existing assignment."""
    assignment = get_object_or_404(Assignment, pk=pk)
    
    # Check if user has permission to edit this assignment
    if not request.user.leagues.filter(id=assignment.meet.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this assignment.')
        return redirect('assignment_list')
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, f'Assignment for {assignment.official.name} updated successfully!')
            return redirect('meet_detail', pk=assignment.meet.pk)
    else:
        form = AssignmentForm(instance=assignment)
        # Limit meet and official choices to those the user has access to if not staff
        if not request.user.is_staff:
            user_leagues = request.user.leagues.all()
            accessible_meets = Meet.objects.filter(league__in=user_leagues)
            form.fields['meet'].queryset = accessible_meets
            
            accessible_officials = Official.objects.filter(team__division__league__in=user_leagues)
            form.fields['official'].queryset = accessible_officials
    
    return render(request, 'officials/assignment_form.html', {
        'form': form,
        'title': 'Update Assignment',
        'assignment': assignment,
    })


@login_required
def assignment_delete(request, pk):
    """Delete an existing assignment."""
    assignment = get_object_or_404(Assignment, pk=pk)
    
    # Check if user has permission to delete this assignment
    if not request.user.leagues.filter(id=assignment.meet.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this assignment.')
        return redirect('assignment_list')
    
    meet_id = assignment.meet.id
    
    if request.method == 'POST':
        official_name = assignment.official.name
        assignment.delete()
        messages.success(request, f'Assignment for {official_name} deleted successfully!')
        return redirect('meet_detail', pk=meet_id)
    
    return render(request, 'officials/assignment_confirm_delete.html', {
        'assignment': assignment,
    })
