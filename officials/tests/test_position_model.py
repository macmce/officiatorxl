from django.test import TestCase
from officials.models import Position, Strategy, Certification


class PositionModelTest(TestCase):
    """Test cases for the Position model."""

    def setUp(self):
        """Set up test data."""
        # Create test certifications with different levels
        self.cert_level_1 = Certification.objects.create(
            name='Level 1',
            abbreviation='L1',
            description='Basic certification',
            level=1
        )
        
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
        
        # Create test strategy
        self.strategy = Strategy.objects.create(
            name='4-person',
            description='Four officials strategy'
        )
        
    def test_position_creation_with_certification(self):
        """Test that a position can be created with a minimum certification."""
        position = Position.objects.create(
            role='Deck Referee',
            strategy=self.strategy,
            location='Pool Deck',
            minimum_certification=self.cert_level_3
        )
        
        # Retrieve from DB to ensure it was saved
        saved_position = Position.objects.get(pk=position.pk)
        
        # Verify all fields
        self.assertEqual(saved_position.role, 'Deck Referee')
        self.assertEqual(saved_position.strategy, self.strategy)
        self.assertEqual(saved_position.location, 'Pool Deck')
        self.assertEqual(saved_position.minimum_certification, self.cert_level_3)
        
    def test_position_creation_without_certification(self):
        """Test that a position can be created without a minimum certification."""
        position = Position.objects.create(
            role='Timer',
            strategy=self.strategy,
            location='Lane 1',
            minimum_certification=None
        )
        
        # Retrieve from DB to ensure it was saved
        saved_position = Position.objects.get(pk=position.pk)
        
        # Verify all fields
        self.assertEqual(saved_position.role, 'Timer')
        self.assertEqual(saved_position.strategy, self.strategy)
        self.assertEqual(saved_position.location, 'Lane 1')
        self.assertIsNone(saved_position.minimum_certification)
        
    def test_position_string_representation(self):
        """Test the string representation of a Position."""
        position = Position.objects.create(
            role='Starter',
            strategy=self.strategy,
            location='Start End',
            minimum_certification=self.cert_level_2
        )
        
        self.assertEqual(str(position), f"Starter ({self.strategy.name})")
        
    def test_update_position_certification(self):
        """Test updating a position's minimum certification."""
        # Create position with Level 1 cert
        position = Position.objects.create(
            role='Stroke Judge',
            strategy=self.strategy,
            location='Turn End',
            minimum_certification=self.cert_level_1
        )
        
        # Update to Level 3 cert
        position.minimum_certification = self.cert_level_3
        position.save()
        
        # Refresh from DB
        position.refresh_from_db()
        
        # Verify certification was updated
        self.assertEqual(position.minimum_certification, self.cert_level_3)
