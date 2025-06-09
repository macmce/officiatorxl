from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView, View
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import render, redirect
import pandas as pd
import io
from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django_filters.views import FilterView

from .models import Position, Strategy
from .forms import PositionForm, PositionImportForm
from .filters import PositionFilter

class PositionListView(LoginRequiredMixin, FilterView):
    model = Position
    template_name = 'officials/position_list.html'
    context_object_name = 'positions'
    paginate_by = 15
    filterset_class = PositionFilter

    def get_queryset(self):
        # Start with the filtered queryset from django-filter
        queryset = super().get_queryset()
        return queryset.select_related('strategy').order_by('strategy__name', 'role')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add filter status flag to indicate if any filters are active
        context['filters_active'] = any(self.request.GET.get(param) for param in self.filterset.form.fields)
        return context

class PositionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Position
    form_class = PositionForm
    template_name = 'officials/position_form.html'
    success_url = reverse_lazy('position_list')
    success_message = "Position '%(role)s' under strategy '%(strategy)s' was created successfully."

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            role=self.object.role,
            strategy=self.object.strategy.get_name_display(),
        )

class PositionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Position
    form_class = PositionForm
    template_name = 'officials/position_form.html'
    success_url = reverse_lazy('position_list')
    success_message = "Position '%(role)s' under strategy '%(strategy)s' was updated successfully."

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            role=self.object.role,
            strategy=self.object.strategy.get_name_display(),
        )

class PositionDeleteView(LoginRequiredMixin, DeleteView):
    model = Position
    template_name = 'officials/position_confirm_delete.html'
    success_url = reverse_lazy('position_list')
    success_message = "Position '%(role)s' under strategy '%(strategy)s' was deleted successfully."

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % {'role': obj.role, 'strategy': obj.strategy.get_name_display()})
        return super(PositionDeleteView, self).delete(request, *args, **kwargs)


class PositionImportView(LoginRequiredMixin, FormView):
    template_name = 'officials/position_import.html'
    form_class = PositionImportForm
    success_url = reverse_lazy('position_list') # Redirect to position list after import

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Import Positions'
        context['form_title'] = 'Upload File to Import Positions'
        context['breadcrumb'] = [
            {'name': 'Dashboard', 'url': reverse('officials_dashboard')},
            {'name': 'Positions', 'url': reverse('position_list')},
            {'name': 'Import Positions'}
        ]
        return context

    def form_valid(self, form):
        # This is where the file processing logic will go.
        import_file = form.cleaned_data['import_file']

        created_count = 0
        skipped_count = 0
        error_count = 0
        errors_list = []

        try:
            if import_file.name.endswith('.xlsx'):
                df = pd.read_excel(import_file, dtype=str).fillna('')
            elif import_file.name.endswith('.csv'):
                df = pd.read_csv(import_file, dtype=str).fillna('')
            else:
                messages.error(self.request, "Unsupported file format. Please use .xlsx or .csv.")
                return self.form_invalid(form)

            expected_columns = ['Role', 'Strategy Name', 'Location'] # All are required
            if not all(col in df.columns for col in expected_columns):
                missing_cols = [col for col in expected_columns if col not in df.columns]
                messages.error(self.request, f"Missing required columns: {', '.join(missing_cols)}. "
                                            f"File must contain 'Role', 'Strategy Name', and 'Location'.")
                return self.form_invalid(form)

            for index, row in df.iterrows():
                row_num = index + 2 # For user-friendly row numbering (1-based index + header)
                role = str(row.get('Role', '')).strip()
                strategy_name = str(row.get('Strategy Name', '')).strip()
                location = str(row.get('Location', '')).strip()  # Location is required

                if not role or not strategy_name or not location:
                    errors_list.append(f"Row {row_num}: 'Role', 'Strategy Name', and 'Location' are required.")
                    error_count += 1
                    continue

                try:
                    strategy = Strategy.objects.get(name=strategy_name)
                except Strategy.DoesNotExist:
                    try:
                        # Attempt to find strategy by display name as a fallback
                        strategy = Strategy.objects.get(name__iexact=strategy_name) # case-insensitive internal name
                    except Strategy.DoesNotExist:
                         # Check if strategy_name matches any of the display names in STRATEGY_CHOICES
                        found_by_display_name = False
                        for choice_value, choice_display in Strategy.STRATEGY_CHOICES:
                            if choice_display.lower() == strategy_name.lower():
                                strategy = Strategy.objects.get(name=choice_value)
                                found_by_display_name = True
                                break
                        if not found_by_display_name:
                            errors_list.append(f"Row {row_num}: Strategy '{strategy_name}' not found.")
                            error_count += 1
                            continue
                except Strategy.MultipleObjectsReturned:
                    errors_list.append(f"Row {row_num}: Multiple strategies found for '{strategy_name}'. Please ensure strategy names are unique or use the internal system name.")
                    error_count += 1
                    continue

                position_data = {
                    'role': role,
                    'strategy': strategy,
                    'location': location
                }

                try:
                    # Always use get_or_create and skip existing positions rather than updating them
                    obj, created = Position.objects.get_or_create(
                        role=role,
                        strategy=strategy,
                        location=location,
                        defaults={}
                    )
                    if created:
                        created_count += 1
                    else:
                        skipped_count += 1
                except IntegrityError as e:
                    errors_list.append(f"Row {row_num} (Role: {role}, Strategy: {strategy.get_name_display()}): Error saving - {e}")
                    error_count += 1
                except Exception as e:
                    errors_list.append(f"Row {row_num} (Role: {role}, Strategy: {strategy.get_name_display()}): Unexpected error - {e}")
                    error_count += 1
            
            if created_count > 0:
                messages.success(self.request, f"{created_count} positions created successfully.")
            if skipped_count > 0:
                messages.info(self.request, f"{skipped_count} positions were skipped because they already exist.")
            
            if error_count > 0:
                error_summary = f"{error_count} errors occurred during import. "
                if errors_list:
                    error_summary += "Details: " + "; ".join(errors_list[:5]) # Show first 5 errors
                    if len(errors_list) > 5:
                        error_summary += " (and more...)"
                messages.error(self.request, error_summary)
                # Optionally, re-render the form if there are errors to show them more prominently
                # return self.form_invalid(form) 
            elif not errors_list and created_count == 0 and skipped_count == 0:
                 messages.info(self.request, "No positions were imported. The file might be empty or all rows were skipped/errored out before processing.")

        except FileNotFoundError:
            messages.error(self.request, "Error: The uploaded file was not found.")
            return self.form_invalid(form)
        except pd.errors.EmptyDataError:
            messages.error(self.request, "The uploaded file is empty or not a valid Excel/CSV file.")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"An unexpected error occurred during file processing: {e}")
            return self.form_invalid(form)

        return super().form_valid(form)


    def form_invalid(self, form):
        messages.error(self.request, "There was an error with your submission. Please check the form.")
        return super().form_invalid(form)


@login_required
def download_position_import_template(request):
    """Generates and serves a sample Excel file for importing positions."""
    # Define sample data for the template
    sample_data = {
        'Role': ['Referee', 'Umpire', 'Linesman', 'Field Judge'],
        'Strategy Name': ['Quadrants', 'Quadrants', 'Sides', 'Quadrants'], # Use actual strategy names or display names
        'Location': ['Backfield', 'Center Field', 'Sideline A', 'Deep Right']
    }
    df = pd.DataFrame(sample_data)

    # Create an in-memory Excel file
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Positions')
    
    excel_buffer.seek(0)

    response = HttpResponse(
        excel_buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="position_import_sample.xlsx"'
    return response
