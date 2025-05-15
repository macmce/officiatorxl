from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from .models import Team, Division, Official, Certification
from .forms import TeamForm, OfficialImportForm
from .filters import TeamFilter
import openpyxl
from openpyxl.utils.exceptions import InvalidFileException
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from io import BytesIO


@login_required
def team_list(request):
    """Display list of teams that the user has access to."""
    user_leagues = request.user.leagues.all()
    initial_teams_queryset = Team.objects.filter(division__league__in=user_leagues).order_by('name')
    
    # Apply the filter
    team_filter = TeamFilter(request.GET, queryset=initial_teams_queryset)
    
    # Paginate the filtered queryset
    paginator = Paginator(team_filter.qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'officials/team_list.html', {
        'page_obj': page_obj,
        'filter': team_filter,
        'filters_active': request.GET and team_filter.form.changed_data
    })


@login_required
def team_detail(request, pk):
    """Display details of a specific team."""
    team = get_object_or_404(Team, pk=pk)
    
    # Check if user has permission to view this team
    if not request.user.leagues.filter(id=team.division.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this team.')
        return redirect('team_list')
    
    # Check if we should show inactive officials
    show_inactive = request.GET.get('show_inactive', 'false').lower() == 'true'
    
    # Get all officials or just active ones based on the filter
    if show_inactive:
        officials = team.officials.all()
    else:
        officials = team.officials.filter(active=True)
    
    # Add import form to the context
    import_form = OfficialImportForm()
    
    return render(request, 'officials/team_detail.html', {
        'team': team,
        'officials': officials,
        'import_form': import_form,
        'show_inactive': show_inactive,
    })


@login_required
def team_create(request):
    """Create a new team."""
    # Only show divisions from leagues the user has access to
    user_leagues = request.user.leagues.all()
    accessible_divisions = Division.objects.filter(league__in=user_leagues)
    
    if not accessible_divisions and not request.user.is_staff:
        messages.error(request, 'You do not have any divisions to add teams to.')
        return redirect('team_list')
    
    if request.method == 'POST':
        form = TeamForm(request.POST, request.FILES)
        if form.is_valid():
            team = form.save(commit=False)
            
            # Check if user has permission to add team to this division
            if not request.user.leagues.filter(id=team.division.league.id).exists() and not request.user.is_staff:
                messages.error(request, 'You do not have permission to add teams to this division.')
                return redirect('team_list')
            
            team.save()
            messages.success(request, f'Team {team.name} created successfully!')
            return redirect('team_detail', pk=team.pk)
    else:
        form = TeamForm()
        # Limit division choices to those the user has access to
        if not request.user.is_staff:
            form.fields['division'].queryset = accessible_divisions
    
    return render(request, 'officials/team_form.html', {
        'form': form,
        'title': 'Create Team',
    })


@login_required
def team_update(request, pk):
    """Update an existing team."""
    team = get_object_or_404(Team, pk=pk)
    
    # Check if user has permission to edit this team
    if not request.user.leagues.filter(id=team.division.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit this team.')
        return redirect('team_list')
    
    if request.method == 'POST':
        form = TeamForm(request.POST, request.FILES, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, f'Team {team.name} updated successfully!')
            return redirect('team_detail', pk=team.pk)
    else:
        form = TeamForm(instance=team)
        # Limit division choices to those the user has access to if not staff
        if not request.user.is_staff:
            user_leagues = request.user.leagues.all()
            form.fields['division'].queryset = Division.objects.filter(league__in=user_leagues)
    
    return render(request, 'officials/team_form.html', {
        'form': form,
        'title': 'Update Team',
        'team': team,
    })


@login_required
def team_delete(request, pk):
    """Delete an existing team."""
    team = get_object_or_404(Team, pk=pk)
    
    # Check if user has permission to delete this team
    if not request.user.leagues.filter(id=team.division.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete this team.')
        return redirect('team_list')
    
    if request.method == 'POST':
        team_name = team.name
        team.delete()
        messages.success(request, f'Team {team_name} deleted successfully!')
        return redirect('team_list')
    
    return render(request, 'officials/team_confirm_delete.html', {
        'team': team,
    })


@login_required
def team_import_officials(request, pk):
    """Import officials from Excel file for a specific team."""
    team = get_object_or_404(Team, pk=pk)
    
    # Check if user has permission to add officials to this team
    if not request.user.leagues.filter(id=team.division.league.id).exists() and not request.user.is_staff:
        messages.error(request, 'You do not have permission to add officials to this team.')
        return redirect('team_list')
    
    if request.method == 'POST':
        form = OfficialImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            
            try:
                # Process Excel file
                wb = openpyxl.load_workbook(excel_file)
                ws = wb.active
                
                # Get column headers
                headers = []
                for i, cell in enumerate(next(ws.iter_rows())):
                    headers.append(cell.value.lower() if cell.value else f"col{i}")
                
                # Make sure required columns exist
                if 'name' not in headers:
                    messages.error(request, 'Excel file must contain a "name" column')
                    return redirect('team_detail', pk=team.pk)
                
                # Track which officials are in the file
                processed_officials = set()
                created_count = 0
                updated_count = 0
                skipped_count = 0
                
                # Process each row
                for row in list(ws.iter_rows())[1:]:  # Skip header row
                    row_data = {}
                    for i, cell in enumerate(row):
                        if i < len(headers):
                            row_data[headers[i]] = cell.value
                    
                    # Skip empty rows
                    if not row_data.get('name'):
                        continue
                    
                    # Create or update official
                    name = row_data.get('name')
                    email = row_data.get('email', '')  # Email is now optional
                    phone = row_data.get('phone', '')
                    proficiency_value = row_data.get('proficiency', 'Beginner')
                    certification_name = row_data.get('certification', None)
                    
                    # Normalize proficiency
                    proficiency_map = {
                        'p': 'Provisional',
                        'provisional': 'Provisional',
                        'b': 'Beginner',
                        'beginner': 'Beginner',
                        'i': 'Intermediate',
                        'intermediate': 'Intermediate',
                        'a': 'Advanced',
                        'advanced': 'Advanced', 
                        'e': 'Expert',
                        'expert': 'Expert'
                    }
                    
                    if isinstance(proficiency_value, str):
                        proficiency = proficiency_map.get(proficiency_value.lower(), 'Beginner')
                    else:
                        proficiency = 'Beginner'
                    
                    # Find certification if provided
                    certification = None
                    if certification_name:
                        try:
                            certification = Certification.objects.get(
                                Q(name__iexact=certification_name) | 
                                Q(abbreviation__iexact=certification_name))
                        except Certification.DoesNotExist:
                            # No matching certification found, it's optional so continue
                            pass
                    
                    # Check if official already exists for this team
                    try:
                        # First look by name and team
                        official = Official.objects.get(name__iexact=name, team=team)
                        
                        # Update existing official
                        if email:
                            official.email = email
                        official.phone = phone
                        official.proficiency = proficiency
                        if certification:
                            official.certification = certification
                        official.active = True  # Activate the official
                        official.save()
                        updated_count += 1
                        
                    except Official.DoesNotExist:
                        # Create new official
                        official = Official(
                            name=name,
                            email=email,
                            phone=phone,
                            proficiency=proficiency,
                            certification=certification,
                            team=team,
                            active=True
                        )
                        official.save()
                        created_count += 1
                    
                    # Track this official as processed
                    processed_officials.add(official.id)
                
                # Deactivate officials not in the file
                deactivated_count = 0
                for official in team.officials.filter(active=True):
                    if official.id not in processed_officials:
                        official.active = False
                        official.save()
                        deactivated_count += 1
                
                # Report results
                messages.success(
                    request, 
                    f'Import successful: {created_count} officials created, {updated_count} updated, '
                    f'{deactivated_count} deactivated.'
                )
                
                return redirect('team_detail', pk=team.pk)
                
            except InvalidFileException:
                messages.error(request, 'Invalid Excel file format. Please upload a valid Excel file.')
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    return redirect('team_detail', pk=team.pk)
