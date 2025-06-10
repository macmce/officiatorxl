from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView, View

from .forms import EventPositionForm, EventPositionInlineFormSet
from .models import Event, EventPosition, Position

class EventPositionListView(LoginRequiredMixin, ListView):
    """View for listing all event positions."""
    model = EventPosition
    template_name = 'officials/event_position_list.html'
    context_object_name = 'event_positions'
    paginate_by = 20

    def get_queryset(self):
        event_id = self.request.GET.get('event_id')
        queryset = EventPosition.objects.all().select_related('event', 'position')
        
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        
        return queryset.order_by('event__event_number', 'position__role')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add events for filtering
        context['events'] = Event.objects.all().order_by('event_number', 'meet_type')
        context['selected_event'] = self.request.GET.get('event_id')
        return context


class EventPositionManageView(LoginRequiredMixin, UpdateView):
    """View for managing positions for a specific event."""
    model = Event
    template_name = 'officials/event_position_manage.html'
    context_object_name = 'event'
    fields = []  # No fields needed for the event form itself
    success_url = reverse_lazy('event-position-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        
        if self.request.POST:
            context['formset'] = EventPositionInlineFormSet(
                self.request.POST, 
                instance=event,
                queryset=EventPosition.objects.filter(event=event).select_related('position')
            )
        else:
            context['formset'] = EventPositionInlineFormSet(
                instance=event,
                queryset=EventPosition.objects.filter(event=event).select_related('position')
            )
            
        # Get all positions for the dropdown
        context['available_positions'] = Position.objects.all().order_by('role')
        
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            formset.save()
            messages.success(self.request, f"Positions for {self.get_object()} have been updated successfully.")
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class EventPositionCreateView(LoginRequiredMixin, View):
    """View for quickly adding a position to an event."""
    
    def post(self, request, *args, **kwargs):
        event_id = request.POST.get('event')
        position_id = request.POST.get('position')
        is_mandatory = request.POST.get('is_mandatory') == 'on'
        
        if not (event_id and position_id):
            messages.error(request, "Both event and position must be selected.")
            return redirect('event-position-list')
            
        event = get_object_or_404(Event, pk=event_id)
        position = get_object_or_404(Position, pk=position_id)
        
        # Check if this combination already exists
        existing = EventPosition.objects.filter(event=event, position=position).first()
        
        if existing:
            existing.is_mandatory = is_mandatory
            existing.save()
            messages.info(request, f"Updated {position.role} for {event}.")
        else:
            EventPosition.objects.create(
                event=event,
                position=position,
                is_mandatory=is_mandatory
            )
            messages.success(request, f"Added {position.role} to {event}.")
            
        return redirect('event-position-list')


class EventPositionQuickAddView(LoginRequiredMixin, View):
    """View for quickly adding multiple positions to an event."""
    template_name = 'officials/event_position_quick_add.html'
    
    def get(self, request, *args, **kwargs):
        events = Event.objects.all().order_by('event_number', 'meet_type')
        positions = Position.objects.all().order_by('strategy__name', 'role')
        
        return render(
            request, 
            self.template_name, 
            {
                'events': events,
                'positions': positions
            }
        )


class AutoAssignPositionsView(LoginRequiredMixin, View):
    """View for automatically assigning standard positions to all events."""
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Collect all position types in a single query with prefetch_related
        all_positions = Position.objects.all()
        
        # Find all position types - using in-memory filtering to reduce queries
        deck_referee_positions = [p for p in all_positions if "Deck Referee".lower() in p.role.lower()]
        starter_positions = [p for p in all_positions if "Starter".lower() in p.role.lower()]
        rto_positions = [p for p in all_positions if "RTO".lower() in p.role.lower()]
        dq_writer_positions = [p for p in all_positions if "DQ Writer".lower() in p.role.lower()]
        oof_positions = [p for p in all_positions if "OOF".lower() in p.role.lower()]
        oof_finish_end_in = [p for p in oof_positions if p.location and "Finish End In".lower() in p.location.lower()]
        verifier_positions = [p for p in all_positions if "Verifier".lower() in p.role.lower()]
        
        # Get all events at once
        all_events = list(Event.objects.all())
        relay_events = [e for e in all_events if "Relay".lower() in e.name.lower()]
        events_25 = [e for e in all_events if "25" in e.name]
        
        # Keep track of which positions were found
        found_positions = []
        if deck_referee_positions:
            found_positions.append(f"Deck Referee ({len(deck_referee_positions)} positions)")
        if starter_positions:
            found_positions.append(f"Starter ({len(starter_positions)} positions)")
        if rto_positions:
            found_positions.append(f"RTO ({len(rto_positions)} positions)")
        if dq_writer_positions:
            found_positions.append(f"DQ Writer ({len(dq_writer_positions)} positions)")
        if oof_positions:
            found_positions.append(f"OOF ({len(oof_positions)} positions)")
            if oof_finish_end_in:
                found_positions.append(f"- Finish End In Location: {len(oof_finish_end_in)} positions")
        if verifier_positions:
            found_positions.append(f"Verifier ({len(verifier_positions)} positions)")
            
        if not found_positions:
            messages.error(request, "Could not find the required positions in the database. Please create these positions first.")
            return redirect('event-list')
        
        # Get all existing event-position assignments to avoid duplicates
        existing_assignments = set()
        for ep in EventPosition.objects.all().values_list('event_id', 'position_id'):
            existing_assignments.add(ep)
        
        # Prepare bulk creation lists
        position_assignments = []
        positions_added = 0
        
        # Process regular (mandatory) positions for all events
        mandatory_positions = deck_referee_positions + starter_positions + dq_writer_positions
        for event in all_events:
            for position in mandatory_positions:
                if (event.id, position.id) not in existing_assignments:
                    position_assignments.append(
                        EventPosition(
                            event=event,
                            position=position,
                            is_mandatory=True
                        )
                    )
                    positions_added += 1
        
        # Process RTO positions for relay events
        for event in relay_events:
            for position in rto_positions:
                # Skip if already assigned
                if (event.id, position.id) in existing_assignments:
                    continue
                    
                # Determine if mandatory based on location
                is_mandatory = False if position.location and "Middle" in position.location else True
                
                position_assignments.append(
                    EventPosition(
                        event=event,
                        position=position,
                        is_mandatory=is_mandatory
                    )
                )
                positions_added += 1
        
        # Process OOF positions with "Finish End In" location for 25 events (mandatory)
        for event in events_25:
            for position in oof_finish_end_in:
                if (event.id, position.id) not in existing_assignments:
                    position_assignments.append(
                        EventPosition(
                            event=event,
                            position=position,
                            is_mandatory=True
                        )
                    )
                    positions_added += 1
        
        # Process optional OOF positions for all events
        for event in all_events:
            for position in oof_positions:
                # Skip if already assigned or if it's a "Finish End In" position for a 25 event
                # (as those were handled as mandatory above)
                if ((event.id, position.id) in existing_assignments or
                    ("25" in event.name and position in oof_finish_end_in)):
                    continue
                    
                position_assignments.append(
                    EventPosition(
                        event=event,
                        position=position,
                        is_mandatory=False
                    )
                )
                positions_added += 1
        
        # Process optional Verifier positions for all events
        for event in all_events:
            for position in verifier_positions:
                if (event.id, position.id) not in existing_assignments:
                    position_assignments.append(
                        EventPosition(
                            event=event,
                            position=position,
                            is_mandatory=False
                        )
                    )
                    positions_added += 1
        
        # Use bulk_create to efficiently insert all positions at once (in batches)
        if position_assignments:
            # Use a batch size to avoid memory issues with very large datasets
            batch_size = 500
            EventPosition.objects.bulk_create(position_assignments, batch_size=batch_size)
        
        if positions_added > 0:
            messages.success(request, f"Successfully assigned positions to events. {positions_added} new assignments created.")
        else:
            messages.info(request, "All events already have the required positions assigned.")
            
        return redirect('event-list')


class RemoveAllEventPositionsView(LoginRequiredMixin, View):
    """View for removing all positions from all events."""
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Get count before deletion for messaging
        position_count = EventPosition.objects.count()
        
        # Delete all event positions
        EventPosition.objects.all().delete()
        
        if position_count > 0:
            messages.success(request, f"Successfully removed all positions from all events. {position_count} assignments were deleted.")
        else:
            messages.info(request, "There were no event positions to remove.")
            
        return redirect('event-list')
