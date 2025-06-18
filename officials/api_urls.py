from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = 'officials_api'

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'leagues', api_views.LeagueViewSet, basename='league')
router.register(r'certifications', api_views.CertificationViewSet, basename='certification')
router.register(r'divisions', api_views.DivisionViewSet, basename='division')
router.register(r'teams', api_views.TeamViewSet, basename='team')
router.register(r'officials', api_views.OfficialViewSet, basename='official')
router.register(r'meets', api_views.MeetViewSet, basename='meet')
router.register(r'pools', api_views.PoolViewSet, basename='pool')
router.register(r'assignments', api_views.AssignmentViewSet, basename='assignment')
router.register(r'events', api_views.EventViewSet, basename='event')
router.register(r'strategies', api_views.StrategyViewSet, basename='strategy')
router.register(r'positions', api_views.PositionViewSet, basename='position')
router.register(r'userleagueadmins', api_views.UserLeagueAdminViewSet, basename='userleagueadmin')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
