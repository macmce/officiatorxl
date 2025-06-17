from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from officials.models import Strategy, Position, Event, EventPosition, Certification

User = get_user_model()


class AutoAssignPositionsTest(TestCase):
    """Test cases for auto-assigning positions to events."""

    def setUp(self):
        """Set up test data."""
        # Create a test user with staff permissions
        self.user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )

        # Create certifications
        self.cert_level_2 = Certification.objects.create(
            name='Level 2',
            abbreviation='L2',
            description='Intermediate certification',
            level=2
        )
        
        self.cert_level_3 = Certification.objects.create(
            name='Level 3',
            abbreviation='L3',
            description='Advanced certification',
            level=3
        )
        
        # Create a test strategy
        self.strategy = Strategy.objects.create(
            name='Full Officials',
            description='Complete team of officials'
        )
        
        # Create regular positions
        self.deck_referee = Position.objects.create(
            role='Deck Referee',
            strategy=self.strategy,
            location='Pool Deck',
            minimum_certification=self.cert_level_3
        )
        
        self.starter = Position.objects.create(
            role='Starter',
            strategy=self.strategy,
            location='Start End',
            minimum_certification=self.cert_level_3
        )
        
        self.dq_writer = Position.objects.create(
            role='DQ Writer',
            strategy=self.strategy,
            location='Admin Table',
            minimum_certification=self.cert_level_2
        )
        
        # Create RTO position for relay events
        self.rto = Position.objects.create(
            role='RTO',
            strategy=self.strategy,
            location='Start End',
            minimum_certification=self.cert_level_2
        )
        
        # Create OOF positions
        self.oof_finish = Position.objects.create(
            role='OOF',
            strategy=self.strategy,
            location='Finish End In',
            minimum_certification=self.cert_level_2
        )
        
        self.oof_turn = Position.objects.create(
            role='OOF',
            strategy=self.strategy,
            location='Turn End',
            minimum_certification=self.cert_level_2
        )
        
        # Create SNT positions
        self.snt_turn = Position.objects.create(
            role='SNT Judge',
            strategy=self.strategy,
            location='Turn End',
            minimum_certification=self.cert_level_2
        )
        
        self.snt_start = Position.objects.create(
            role='SNT Referee',
            strategy=self.strategy,
            location='Start End',
            minimum_certification=self.cert_level_3
        )
        
        # Create test events
        self.freestyle_50 = Event.objects.create(
            event_number=1,
            name='Freestyle 50m',
            description='50m freestyle',
            meet_type='dual',
            gender='mixed'
        )
        
        self.relay_event = Event.objects.create(
            event_number=2,
            name='Freestyle Relay 4x100m',
            description='4x100m freestyle relay',
            meet_type='dual',
            gender='mixed'
        )
        
        self.event_25 = Event.objects.create(
            event_number=3,
            name='Butterfly 25m',
            description='25m butterfly',
            meet_type='dual',
            gender='mixed'
        )
        
        # Set up the test client
        self.client = Client()
        self.auto_assign_url = reverse('auto-assign-positions')
        
    def test_auto_assign_requires_login(self):
        """Test that auto-assign view requires login."""
        response = self.client.post(self.auto_assign_url)
        self.assertEqual(response.status_code, 302)  # Redirects to login
        
    def test_auto_assign_requires_staff(self):
        """Test that auto-assign view requires staff permissions."""
        # Create a regular non-staff user
        regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='regularpass123'
        )
        
        # Login as the regular user
        self.client.login(username='regularuser', password='regularpass123')
        
        # Try to access the auto-assign view
        response = self.client.post(self.auto_assign_url)
        
        # Should redirect (not have permission)
        self.assertEqual(response.status_code, 302)
        
    def test_auto_assign_snt_positions(self):
        """Test that SNT positions are auto-assigned according to the rules."""
        # Login as staff user
        self.client.login(username='staffuser', password='staffpass123')
        
        # Execute auto-assign
        response = self.client.post(self.auto_assign_url)
        
        # Should redirect to event list
        self.assertEqual(response.status_code, 302)
        
        # Check SNT Turn positions (should be assigned to ALL events as mandatory)
        # For Freestyle 50m
        freestyle_snt_turn = EventPosition.objects.filter(
            event=self.freestyle_50,
            position=self.snt_turn
        ).first()
        self.assertIsNotNone(freestyle_snt_turn)
        self.assertTrue(freestyle_snt_turn.is_mandatory)
        
        # For Relay event
        relay_snt_turn = EventPosition.objects.filter(
            event=self.relay_event,
            position=self.snt_turn
        ).first()
        self.assertIsNotNone(relay_snt_turn)
        self.assertTrue(relay_snt_turn.is_mandatory)
        
        # For 25m event
        event_25_snt_turn = EventPosition.objects.filter(
            event=self.event_25,
            position=self.snt_turn
        ).first()
        self.assertIsNotNone(event_25_snt_turn)
        self.assertTrue(event_25_snt_turn.is_mandatory)
        
        # Check SNT Start positions (should be assigned to non-25 events as mandatory)
        # For Freestyle 50m (should be assigned)
        freestyle_snt_start = EventPosition.objects.filter(
            event=self.freestyle_50,
            position=self.snt_start
        ).first()
        self.assertIsNotNone(freestyle_snt_start)
        self.assertTrue(freestyle_snt_start.is_mandatory)
        
        # For Relay event (should be assigned)
        relay_snt_start = EventPosition.objects.filter(
            event=self.relay_event,
            position=self.snt_start
        ).first()
        self.assertIsNotNone(relay_snt_start)
        self.assertTrue(relay_snt_start.is_mandatory)
        
        # For 25m event (should NOT be assigned)
        event_25_snt_start = EventPosition.objects.filter(
            event=self.event_25,
            position=self.snt_start
        ).first()
        self.assertIsNone(event_25_snt_start)
        
    def test_mandatory_positions_assignment(self):
        """Test that regular mandatory positions are correctly assigned."""
        # Login as staff user
        self.client.login(username='staffuser', password='staffpass123')
        
        # Execute auto-assign
        self.client.post(self.auto_assign_url)
        
        # Check all events have Deck Referee, Starter, and DQ Writer as mandatory
        for event in [self.freestyle_50, self.relay_event, self.event_25]:
            # Deck Referee
            deck_ref_assigned = EventPosition.objects.filter(
                event=event,
                position=self.deck_referee,
                is_mandatory=True
            ).exists()
            self.assertTrue(deck_ref_assigned)
            
            # Starter
            starter_assigned = EventPosition.objects.filter(
                event=event,
                position=self.starter,
                is_mandatory=True
            ).exists()
            self.assertTrue(starter_assigned)
            
            # DQ Writer
            dq_writer_assigned = EventPosition.objects.filter(
                event=event,
                position=self.dq_writer,
                is_mandatory=True
            ).exists()
            self.assertTrue(dq_writer_assigned)
    
    def test_relay_specific_positions(self):
        """Test that relay-specific positions are only assigned to relay events."""
        # Login as staff user
        self.client.login(username='staffuser', password='staffpass123')
        
        # Execute auto-assign
        self.client.post(self.auto_assign_url)
        
        # Check RTO is assigned to relay event
        relay_rto = EventPosition.objects.filter(
            event=self.relay_event,
            position=self.rto
        ).exists()
        self.assertTrue(relay_rto)
        
        # Check RTO is NOT assigned to non-relay events
        freestyle_rto = EventPosition.objects.filter(
            event=self.freestyle_50,
            position=self.rto
        ).exists()
        self.assertFalse(freestyle_rto)
        
        event_25_rto = EventPosition.objects.filter(
            event=self.event_25,
            position=self.rto
        ).exists()
        self.assertFalse(event_25_rto)
        
    def test_25m_specific_positions(self):
        """Test that 25m-specific positions are only assigned to 25m events."""
        # Login as staff user
        self.client.login(username='staffuser', password='staffpass123')
        
        # Execute auto-assign
        self.client.post(self.auto_assign_url)
        
        # Check OOF Finish End In is assigned to 25m event as mandatory
        event_25_oof_finish = EventPosition.objects.filter(
            event=self.event_25,
            position=self.oof_finish,
            is_mandatory=True
        ).exists()
        self.assertTrue(event_25_oof_finish)
        
    def test_no_duplicate_assignments(self):
        """Test that auto-assign doesn't create duplicate assignments."""
        # Login as staff user
        self.client.login(username='staffuser', password='staffpass123')
        
        # Execute auto-assign twice
        self.client.post(self.auto_assign_url)
        response = self.client.post(self.auto_assign_url)
        
        # Check that the second call doesn't create duplicates
        # Count all assignments for a specific event-position pair
        count = EventPosition.objects.filter(
            event=self.freestyle_50,
            position=self.snt_turn
        ).count()
        
        # Should only be one assignment
        self.assertEqual(count, 1)
