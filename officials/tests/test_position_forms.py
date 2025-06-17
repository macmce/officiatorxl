from django.test import TestCase
from officials.models import Strategy, Certification, Position
from officials.forms import PositionForm


class PositionFormTest(TestCase):
    """Test cases for the PositionForm."""

    def setUp(self):
        """Set up test data."""
        # Create certifications with different levels
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
        
        # Create a test strategy
        self.strategy = Strategy.objects.create(
            name='Standard',
            description='Standard strategy'
        )

    def test_form_initialization(self):
        """Test that the form is initialized with correct fields and queryset."""
        form = PositionForm()
        
        # Check that the form has the minimum_certification field
        self.assertIn('minimum_certification', form.fields)
        
        # Check that the queryset is ordered by level and name
        queryset = form.fields['minimum_certification'].queryset
        self.assertEqual(list(queryset), list(Certification.objects.all().order_by('level', 'name')))
        
        # Check that empty_label is set correctly
        self.assertEqual(form.fields['minimum_certification'].empty_label, "No Minimum Certification")
        
        # Check that the widget has the correct CSS class
        self.assertEqual(
            form.fields['minimum_certification'].widget.attrs['class'], 
            'form-select'
        )
        
    def test_form_default_certification(self):
        """Test that the form defaults to level 3 certification if available."""
        form = PositionForm()
        
        # Check that level 3 is set as the default
        # Use filter instead of get since there may be multiple level 3 certifications
        cert_level_3 = Certification.objects.filter(level=3).first()
        self.assertEqual(form.initial.get('minimum_certification'), cert_level_3.id)
        
    def test_form_validation_with_certification(self):
        """Test form validation with a minimum certification specified."""
        form_data = {
            'role': 'Referee',
            'strategy': self.strategy.id,
            'location': 'Pool Deck',
            'minimum_certification': self.cert_level_3.id
        }
        
        form = PositionForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_form_validation_without_certification(self):
        """Test form validation without a minimum certification specified."""
        form_data = {
            'role': 'Timer',
            'strategy': self.strategy.id,
            'location': 'Lane 1',
            # No minimum_certification specified
        }
        
        form = PositionForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Save the form and check that minimum_certification is None
        position = form.save(commit=False)
        self.assertIsNone(position.minimum_certification)
        
    def test_form_with_empty_certification(self):
        """Test form with an empty string for minimum certification."""
        form_data = {
            'role': 'Stroke Judge',
            'strategy': self.strategy.id,
            'location': 'Side of Pool',
            'minimum_certification': ''  # Empty string
        }
        
        form = PositionForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Save the form and check that minimum_certification is None
        position = form.save(commit=False)
        self.assertIsNone(position.minimum_certification)
        
    def test_form_with_instance_and_certification(self):
        """Test initializing the form with an instance that has a minimum certification."""
        # Create a form instance with an existing model instance
        instance = Position.objects.create(
            role='Starter',
            strategy=self.strategy,
            location='Start End',
            minimum_certification=self.cert_level_2
        )
        
        form = PositionForm(instance=instance)
        
        # The initial value should be the instance's certification, not the default
        self.assertEqual(form.initial['minimum_certification'], self.cert_level_2.id)
        
    def test_form_with_instance_without_certification(self):
        """Test initializing the form with an instance that has no minimum certification."""
        # Create a form instance with an existing model instance that has no certification
        instance = Position.objects.create(
            role='Timer',
            strategy=self.strategy,
            location='Timing Area',
            minimum_certification=None
        )
        
        form = PositionForm(instance=instance)
        
        # With no certification specified, level 3 should be the default
        cert_level_3 = Certification.objects.filter(level=3).first()  # Avoid MultipleObjectsReturned
        self.assertEqual(form.initial.get('minimum_certification'), cert_level_3.id)
