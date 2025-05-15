from django.test import TestCase
from officials.models import Event
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction

class EventModelTest(TestCase):
    """Test cases for the Event model."""
    
    def setUp(self):
        """Set up test data."""
        self.event_data = {
            'event_number': 1,
            'name': 'Test Event',
            'description': 'Test Description',
            'meet_type': 'dual',
            'gender': 'male'
        }

    def test_create_event(self):
        """Test creating an event with valid data."""
        event = Event.objects.create(**self.event_data)
        self.assertEqual(event.name, 'Test Event')
        self.assertEqual(event.event_number, 1)
        self.assertEqual(event.meet_type, 'dual')
        self.assertEqual(event.gender, 'male')
        self.assertEqual(str(event), "1 - Test Event")

    def test_create_event_without_description(self):
        """Test creating an event without a description (should be optional)."""
        data = self.event_data.copy()
        data.pop('description')
        event = Event.objects.create(**data)
        # Django may store empty values as '' rather than None
        self.assertTrue(event.description == '' or event.description is None)

    def test_event_number_validation(self):
        """Test that event_number is validated to be between 1-99."""
        # Test value below minimum
        data = self.event_data.copy()
        data['event_number'] = 0
        
        with self.assertRaises(ValidationError):
            event = Event(**data)
            event.full_clean()  # This should raise ValidationError
        
        # Test value above maximum
        data['event_number'] = 100
        
        with self.assertRaises(ValidationError):
            event = Event(**data)
            event.full_clean()  # This should raise ValidationError

    def test_unique_constraint(self):
        """Test the unique constraint on event_number + meet_type."""
        # Create the first event
        Event.objects.create(**self.event_data)
        
        # Try to create a second event with the same event_number and meet_type
        data = self.event_data.copy()
        data['name'] = 'Different Name'
        
        # This should raise an IntegrityError
        # Use transaction.atomic to handle the expected database error properly
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Event.objects.create(**data)
        
        # Should be able to create with same number but different meet_type
        data = self.event_data.copy()
        data['meet_type'] = 'divisional'
        Event.objects.create(**data)
        self.assertEqual(Event.objects.count(), 2)
        
        # Should be able to create with different number but same meet_type
        data = self.event_data.copy()
        data['event_number'] = 2
        Event.objects.create(**data)
        self.assertEqual(Event.objects.count(), 3)

    def test_ordering(self):
        """Test that events are ordered by event_number, then meet_type."""
        # Create events in non-sequential order
        Event.objects.create(event_number=3, name='Event 3', meet_type='dual', gender='male')
        Event.objects.create(event_number=1, name='Event 1', meet_type='divisional', gender='female')
        Event.objects.create(event_number=1, name='Event 1', meet_type='dual', gender='male')
        Event.objects.create(event_number=2, name='Event 2', meet_type='dual', gender='female')
        
        events = list(Event.objects.all())
        
        # Check ordering - event_number is primary sort key
        self.assertEqual(events[0].event_number, 1)
        self.assertEqual(events[1].event_number, 1)
        self.assertEqual(events[2].event_number, 2)
        self.assertEqual(events[3].event_number, 3)
        
        # For same event_number, meet_type is sorted alphabetically ('divisional' before 'dual')
        self.assertEqual(events[0].meet_type, 'divisional')
        self.assertEqual(events[1].meet_type, 'dual')
