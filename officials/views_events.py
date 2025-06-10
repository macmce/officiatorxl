from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django import forms
from django.contrib import messages
import os # For file path joining
from django.conf import settings # To get BASE_DIR
from django_filters.views import FilterView

# Import services
from .services.event_importer import EventImporter

# Import models, filters and forms
from .models import Event, Meet
from .filters import EventFilter
from .forms import EventForm, EventImportForm, EventFilterForm

class EventListView(LoginRequiredMixin, FilterView):
    model = Event
    template_name = 'officials/event_list.html'
    context_object_name = 'events'
    paginate_by = 10 
    filterset_class = EventFilter

    def get_queryset(self):
        # Start with the filtered queryset from django-filter
        queryset = super().get_queryset()
        
        # Prefetch related event positions for counting
        queryset = queryset.prefetch_related('event_positions')
        
        # Order events by event_number, then meet_type
        return queryset.order_by('event_number', 'meet_type')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter status flag to indicate if any filters are active
        context['filters_active'] = any(self.request.GET.get(param) for param in self.filterset.form.fields)
        
        return context
        
    def render_to_response(self, context, **response_kwargs):
        # Override to ensure standard Django template rendering
        accept_header = self.request.META.get('HTTP_ACCEPT', '')
        
        # For regular browser requests or explicit HTML requests, use Django template rendering
        if 'text/html' in accept_header or not ('application/json' in accept_header or 'application/xml' in accept_header):
            return super().render_to_response(context, **response_kwargs)
            
        # For API requests, let DRF handle it
        return super().render_to_response(context, **response_kwargs)

class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'officials/event_detail.html'
    context_object_name = 'event'
    
    def get_queryset(self):
        # Prefetch related event_positions and their positions
        return super().get_queryset().prefetch_related(
            'event_positions__position',
            'event_positions__position__strategy'
        )
    
    def render_to_response(self, context, **response_kwargs):
        # Override to ensure standard Django template rendering
        accept_header = self.request.META.get('HTTP_ACCEPT', '')
        
        # For regular browser requests or explicit HTML requests, use Django template rendering
        if 'text/html' in accept_header or not ('application/json' in accept_header or 'application/xml' in accept_header):
            return super().render_to_response(context, **response_kwargs)
            
        # For API requests, let DRF handle it
        return super().render_to_response(context, **response_kwargs)

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'officials/event_form.html'
    success_url = reverse_lazy('event-list')
    
    def render_to_response(self, context, **response_kwargs):
        # Override to ensure standard Django template rendering
        accept_header = self.request.META.get('HTTP_ACCEPT', '')
        
        # For regular browser requests or explicit HTML requests, use Django template rendering
        if 'text/html' in accept_header or not ('application/json' in accept_header or 'application/xml' in accept_header):
            return super().render_to_response(context, **response_kwargs)
            
        # For API requests, let DRF handle it
        return super().render_to_response(context, **response_kwargs)

class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'officials/event_form.html'
    success_url = reverse_lazy('event-list')
    
    def render_to_response(self, context, **response_kwargs):
        # Override to ensure standard Django template rendering
        accept_header = self.request.META.get('HTTP_ACCEPT', '')
        
        # For regular browser requests or explicit HTML requests, use Django template rendering
        if 'text/html' in accept_header or not ('application/json' in accept_header or 'application/xml' in accept_header):
            return super().render_to_response(context, **response_kwargs)
            
        # For API requests, let DRF handle it
        return super().render_to_response(context, **response_kwargs)

class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = 'officials/event_confirm_delete.html'
    success_url = reverse_lazy('event-list')
    
    def render_to_response(self, context, **response_kwargs):
        # Override to ensure standard Django template rendering
        accept_header = self.request.META.get('HTTP_ACCEPT', '')
        
        # For regular browser requests or explicit HTML requests, use Django template rendering
        if 'text/html' in accept_header or not ('application/json' in accept_header or 'application/xml' in accept_header):
            return super().render_to_response(context, **response_kwargs)
            
        # For API requests, let DRF handle it
        return super().render_to_response(context, **response_kwargs)

class EventImportView(LoginRequiredMixin, FormView):
    template_name = 'officials/event_import.html'
    form_class = EventImportForm
    success_url = reverse_lazy('event-list')
    
    def render_to_response(self, context, **response_kwargs):
        # Override to ensure standard Django template rendering
        accept_header = self.request.META.get('HTTP_ACCEPT', '')
        
        # For regular browser requests or explicit HTML requests, use Django template rendering
        if 'text/html' in accept_header or not ('application/json' in accept_header or 'application/xml' in accept_header):
            return super().render_to_response(context, **response_kwargs)
            
        # For API requests, let DRF handle it
        return super().render_to_response(context, **response_kwargs)

    def form_valid(self, form):
        uploaded_file = form.cleaned_data['file']
        replace_all = self.request.POST.get('replace') == 'on'
        
        try:
            # Use our service to handle the import
            importer = EventImporter(replace_all=replace_all)
            result = importer.import_events(uploaded_file)
            
            # Display appropriate messages based on the import result
            if result.success_count > 0:
                messages.success(
                    self.request, 
                    f"Import completed: {result.created_count} events created, {result.updated_count} events updated, "
                    f"{result.skipped_count} rows skipped, {result.error_count} errors."
                )
            else:
                messages.warning(self.request, "No events were imported.")
            
            # Show errors if any
            if result.errors:
                messages.error(self.request, "Errors occurred during import:")
                for error in result.errors[:10]:  # Show first 10 errors to avoid overwhelming the user
                    messages.error(self.request, error)
                
                if len(result.errors) > 10:
                    messages.error(self.request, f"...and {len(result.errors) - 10} more errors. Please check your file.")
            
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(self.request, f"Error processing file: {str(e)}")
            return super().form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error with the uploaded file. Please check the file format and try again.')
        return super().form_invalid(form)

class EventDeleteAllView(LoginRequiredMixin, View):
    template_name = 'officials/event_delete_all.html'

    def get(self, request, *args, **kwargs):
        event_count = Event.objects.count() if hasattr(Event, 'objects') else 0
        return render(request, self.template_name, {'event_count': event_count})

    def post(self, request, *args, **kwargs):
        return HttpResponse('Placeholder: All events would be deleted. Action not implemented yet. <a href="' + str(reverse_lazy('event-list')) + '">Back to list</a>')


class EventDeleteSelectedView(LoginRequiredMixin, View):
    """View to handle the deletion of selected events."""
    
    def post(self, request, *args, **kwargs):
        selected_ids = request.POST.getlist('selected_events')
        
        if not selected_ids:
            messages.warning(request, 'No events were selected for deletion.')
            return redirect('event-list')
        
        try:
            # Get the count before deletion for the success message
            count = Event.objects.filter(pk__in=selected_ids).count()
            
            # Delete the selected events
            Event.objects.filter(pk__in=selected_ids).delete()
            
            # Success message
            messages.success(request, f'{count} event(s) successfully deleted.')
        except Exception as e:
            # Error message if deletion fails
            messages.error(request, f'Error deleting events: {str(e)}')
        
        return redirect('event-list')

class DownloadEventTemplateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            # Use the service to generate a template dynamically
            workbook = EventImporter.generate_template()
            
            # Create response with the workbook content
            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response['Content-Disposition'] = 'attachment; filename="event_import_template.xlsx"'
            
            # Save the workbook to the response
            workbook.save(response)
            return response
            
        except Exception as e:
            messages.error(request, f"Error generating template: {str(e)}")
            return redirect('event-import')
