from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator


class UserLeagueAdmin(models.Model):
    """Model to track which users are admins for which leagues."""
    class RoleChoices(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        EDITOR = 'EDITOR', 'Editor'
        VIEWER = 'VIEWER', 'Viewer'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='league_admin_roles')
    league = models.ForeignKey('League', on_delete=models.CASCADE, related_name='league_admins')
    role = models.CharField(
        max_length=10,
        choices=RoleChoices.choices,
        default=RoleChoices.VIEWER,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'league')
        verbose_name = 'League Admin'
        verbose_name_plural = 'League Admins'
    
    def __str__(self):
        return f"{self.user.username} - {self.league.name} ({self.get_role_display()})"


class Certification(models.Model):
    """Model for official certifications."""
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=3, blank=True)
    description = models.TextField(blank=True)
    level = models.PositiveSmallIntegerField(default=1)
    
    def __str__(self):
        return self.name


class League(models.Model):
    """Model for swim leagues."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    logo = models.ImageField(upload_to='league_logos', blank=True, null=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='leagues', blank=True)
    
    def __str__(self):
        return self.name


class Division(models.Model):
    """Model for divisions within leagues."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='divisions')
    
    def __str__(self):
        return f"{self.name} - {self.league.name}"


class Pool(models.Model):
    """Model for swimming pools."""
    UNIT_CHOICES = [
        ('Yards', 'Yards'),
        ('Meters', 'Meters'),
    ]
    
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    length = models.PositiveSmallIntegerField(default=50, help_text="Pool length")
    units = models.CharField(max_length=6, choices=UNIT_CHOICES, default='Yards')
    lanes = models.PositiveSmallIntegerField(default=6, help_text="Number of lanes")
    bidirectional = models.BooleanField(default=False, help_text="Do you start events at both ends of the pool?")
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='pools')
    
    def __str__(self):
        return f"{self.name} ({self.length} {self.units}, {self.lanes} lanes)"


class Team(models.Model):
    """Model for swim teams."""
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10, blank=True)
    mascot = models.CharField(max_length=50, blank=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='teams')
    logo = models.ImageField(upload_to='team_logos', blank=True, null=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='teams', blank=True)
    
    def __str__(self):
        return self.name


class Official(models.Model):
    """Model for swim meet officials."""
    PROFICIENCY_CHOICES = [
        ('Provisional', 'Provisional'),
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Expert', 'Expert'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    certification = models.ForeignKey(Certification, on_delete=models.SET_NULL, null=True, related_name='officials')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='officials')
    active = models.BooleanField(default=True)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='Beginner')
    
    def __str__(self):
        return self.name


class Meet(models.Model):
    """Model for swim meets."""
    MEET_TYPE_CHOICES = [
        ('dual', 'Dual'),
        ('divisional', 'Divisional'),
        ('invitational', 'Invitational')
    ]
    
    name = models.CharField(max_length=200)
    date = models.DateField()
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='meets')
    host_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='hosted_meets')
    pool = models.ForeignKey('Pool', on_delete=models.SET_NULL, null=True, blank=True, related_name='meets')
    participating_teams = models.ManyToManyField(Team, related_name='meets')
    meet_type = models.CharField(max_length=20, choices=MEET_TYPE_CHOICES, default='dual')
    weather_forecast = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.date}"


class Assignment(models.Model):
    """Model for official assignments to meets."""
    meet = models.ForeignKey(Meet, on_delete=models.CASCADE, related_name='assignments')
    official = models.ForeignKey(Official, on_delete=models.CASCADE, related_name='assignments')
    role = models.CharField(max_length=100)
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    confirmed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('meet', 'official', 'role')
    
    def __str__(self):
        return f"{self.official} - {self.role} at {self.meet}"


class Event(models.Model):
    MEET_TYPE_CHOICES = [
        ('dual', 'Dual'),
        ('divisional', 'Divisional'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    event_number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)],
        help_text="Event number between 1-99",
        default=1
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    meet_type = models.CharField(
        max_length=20, 
        choices=MEET_TYPE_CHOICES,
        default='dual'
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='male'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('event_number', 'meet_type')
        ordering = ['event_number', 'meet_type']
    
    def __str__(self):
        return f"{self.event_number} - {self.name}"


class Strategy(models.Model):
    """Model for officiating strategies."""
    STRATEGY_CHOICES = [
        ('QUADRANTS', 'Quadrants'),
        ('SIDES', 'Sides'),
    ]
    
    name = models.CharField(
        max_length=20, 
        choices=STRATEGY_CHOICES,
        unique=True,
        help_text="Officiating strategy (Quadrants or Sides)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Strategy'
        verbose_name_plural = 'Strategies'
        ordering = ['name']

    def __str__(self):
        return self.get_name_display()


class Position(models.Model):
    """Model for officiating positions within a strategy."""
    role = models.CharField(
        max_length=100,
        help_text="The name or title of the position (e.g., Referee, Head Linesman, Side Judge)"
    )
    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.CASCADE,
        related_name='positions',
        help_text="The officiating strategy this position belongs to"
    )
    location = models.CharField(
        max_length=100,
        help_text="Typical on-field location or area of responsibility for this position (e.g., Backfield, Sideline, Deep Wing)"
    )
    minimum_certification = models.ForeignKey(
        Certification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='required_positions',
        help_text="The minimum certification level required for this position"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Add many-to-many relationship to Event through EventPosition
    events = models.ManyToManyField(
        'Event',
        through='EventPosition',
        related_name='positions'
    )

    class Meta:
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'
        ordering = ['strategy', 'role']
        unique_together = ('role', 'strategy', 'location') # A role should be unique within a given strategy and location

    def __str__(self):
        return f"{self.role} ({self.strategy.name})"


class EventPosition(models.Model):
    """Model for associating positions with events and indicating whether they're mandatory."""
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='event_positions',
        help_text="Event that requires this position"
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='event_positions',
        help_text="Position required for this event"
    )
    is_mandatory = models.BooleanField(
        default=True,
        help_text="Indicates if this position is mandatory for the event"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Event Position'
        verbose_name_plural = 'Event Positions'
        unique_together = ('event', 'position')
        ordering = ['event', 'position']

    def __str__(self):
        mandatory_status = "Mandatory" if self.is_mandatory else "Optional"
        return f"{self.position.role} for {self.event} ({mandatory_status})"
