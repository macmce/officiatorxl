from django.contrib import admin
from .models import Certification, League, Division, Team, Pool, Official, Meet, Assignment, UserLeagueAdmin, Strategy, Position


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'level', 'description')
    search_fields = ('name',)
    ordering = ('level', 'name')


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'founded_year', 'description')
    search_fields = ('name',)


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'league', 'description')
    list_filter = ('league',)
    search_fields = ('name',)


@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'length', 'units', 'lanes', 'bidirectional')
    list_filter = ('units', 'bidirectional', 'team')
    search_fields = ('name', 'address')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'abbreviation', 'division')
    list_filter = ('division__league', 'division')
    search_fields = ('name', 'abbreviation')


@admin.register(Official)
class OfficialAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'certification', 'active', 'proficiency')
    list_filter = ('active', 'certification', 'team')
    search_fields = ('name', 'email')


@admin.register(Meet)
class MeetAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'meet_type', 'league', 'host_team')
    list_filter = ('league', 'date', 'meet_type')
    search_fields = ('name',)
    date_hierarchy = 'date'
    filter_horizontal = ('participating_teams',)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('meet', 'official', 'role', 'assigned_at', 'confirmed')
    list_filter = ('confirmed', 'meet', 'role')
    search_fields = ('official__last_name', 'official__first_name', 'meet__name')
    date_hierarchy = 'assigned_at'


@admin.register(UserLeagueAdmin)
class UserLeagueAdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'league', 'created_at')
    list_filter = ('league',)
    search_fields = ('user__username', 'user__email', 'league__name')
    raw_id_fields = ('user', 'league')


@admin.register(Strategy)
class StrategyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('role', 'strategy', 'location', 'created_at', 'updated_at')
    list_filter = ('strategy',)
    search_fields = ('role', 'location', 'strategy__name')
    autocomplete_fields = ['strategy']
