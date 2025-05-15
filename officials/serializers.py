from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import League, Certification, Division, Team, Official, Meet, Pool, Assignment, Event, Strategy, Position, UserLeagueAdmin

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class LeagueSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True) # Or use serializers.PrimaryKeyRelatedField for writable

    class Meta:
        model = League
        fields = ['id', 'name', 'description', 'founded_year', 'logo', 'users']

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id', 'name', 'abbreviation', 'description', 'level']


class DivisionSerializer(serializers.ModelSerializer):
    league = serializers.PrimaryKeyRelatedField(queryset=League.objects.all())
    # To show nested League details instead of just ID:
    # league = LeagueSerializer(read_only=True) 

    class Meta:
        model = Division
        fields = ['id', 'name', 'description', 'league']


class TeamSerializer(serializers.ModelSerializer):
    division = serializers.PrimaryKeyRelatedField(queryset=Division.objects.all())
    users = UserSerializer(many=True, read_only=True) # Or PrimaryKeyRelatedField for writable
    # To show nested Division details:
    # division = DivisionSerializer(read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'abbreviation', 'mascot', 'division', 'logo', 'address', 'website', 'users']


class OfficialSerializer(serializers.ModelSerializer):
    certification = serializers.PrimaryKeyRelatedField(queryset=Certification.objects.all(), allow_null=True)
    team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all())
    # To show nested details:
    # certification = CertificationSerializer(read_only=True)
    # team = TeamSerializer(read_only=True)

    class Meta:
        model = Official
        fields = ['id', 'name', 'email', 'phone', 'certification', 'team', 'active', 'proficiency']


class PoolSerializer(serializers.ModelSerializer):
    team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all())
    # To show nested Team details:
    # team = TeamSerializer(read_only=True)

    class Meta:
        model = Pool
        fields = ['id', 'name', 'address', 'length', 'units', 'lanes', 'bidirectional', 'team']


class MeetSerializer(serializers.ModelSerializer):
    league = serializers.PrimaryKeyRelatedField(queryset=League.objects.all())
    host_team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all())
    pool = serializers.PrimaryKeyRelatedField(queryset=Pool.objects.all(), allow_null=True, required=False)
    participating_teams = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all(), many=True)
    # To show nested details:
    # league = LeagueSerializer(read_only=True)
    # host_team = TeamSerializer(read_only=True)
    # pool = PoolSerializer(read_only=True)
    # participating_teams = TeamSerializer(many=True, read_only=True)

    class Meta:
        model = Meet
        fields = ['id', 'name', 'date', 'league', 'host_team', 'pool', 'participating_teams', 'meet_type', 'weather_forecast']


class AssignmentSerializer(serializers.ModelSerializer):
    meet = serializers.PrimaryKeyRelatedField(queryset=Meet.objects.all())
    official = serializers.PrimaryKeyRelatedField(queryset=Official.objects.all())
    assigned_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'meet', 'official', 'role', 'assigned_at', 'notes', 'confirmed']


class EventSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'event_number', 'name', 'description', 'meet_type', 'gender', 'created_at', 'updated_at']


class StrategySerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Strategy
        fields = ['id', 'name', 'created_at', 'updated_at']


class PositionSerializer(serializers.ModelSerializer):
    strategy = serializers.PrimaryKeyRelatedField(queryset=Strategy.objects.all())
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Position
        fields = ['id', 'role', 'strategy', 'location', 'created_at', 'updated_at']


class UserLeagueAdminSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    league = serializers.PrimaryKeyRelatedField(queryset=League.objects.all())
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = UserLeagueAdmin
        fields = ['id', 'user', 'league', 'role', 'created_at']
