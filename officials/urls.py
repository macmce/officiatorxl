from django.urls import path
from . import views
from . import api_views
from . import views_events
from . import views_strategy
from . import views_position
from . import views_leagues
from . import views_meets
from . import views_event_positions

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='officials_dashboard'),
    
    # League URLs
    path('leagues/', views_leagues.LeagueListView.as_view(), name='league_list'),
    path('leagues/<int:pk>/', views_leagues.league_detail, name='league_detail'),
    path('leagues/create/', views_leagues.league_create, name='league_create'),
    path('leagues/<int:pk>/update/', views_leagues.league_update, name='league_update'),
    path('leagues/<int:pk>/delete/', views_leagues.league_delete, name='league_delete'),
    
    # Division URLs
    path('divisions/', views.division_list, name='division_list'),
    path('divisions/<int:pk>/', views.division_detail, name='division_detail'),
    path('divisions/create/', views.division_create, name='division_create'),
    path('divisions/<int:pk>/update/', views.division_update, name='division_update'),
    path('divisions/<int:pk>/delete/', views.division_delete, name='division_delete'),
    
    # Team URLs
    path('teams/', views.team_list, name='team_list'),
    path('teams/<int:pk>/', views.team_detail, name='team_detail'),
    path('teams/create/', views.team_create, name='team_create'),
    path('teams/<int:pk>/update/', views.team_update, name='team_update'),
    path('teams/<int:pk>/delete/', views.team_delete, name='team_delete'),
    path('teams/<int:pk>/import/', views.team_import_officials, name='team_import_officials'),
    path('teams/<int:pk>/export/excel/', views.export_team_officials_excel, name='export_team_officials_excel'),
    path('teams/<int:pk>/export/json/', views.export_team_officials_json, name='export_team_officials_json'),
    path('teams/<int:team_id>/pools/create/', views.pool_create, name='pool_create'),
    path('pools/<int:pk>/update/', views.pool_update, name='pool_update'),
    path('pools/<int:pk>/delete/', views.pool_delete, name='pool_delete'),
    path('officials-template/', views.generate_officials_template, name='generate_officials_template'),
    
    # Official URLs
    path('officials/', views.official_list, name='official_list'),
    path('officials/<int:pk>/', views.official_detail, name='official_detail'),
    path('officials/create/', views.official_create, name='official_create'),
    path('officials/<int:pk>/update/', views.official_update, name='official_update'),
    path('officials/<int:pk>/delete/', views.official_delete, name='official_delete'),
    
    # Certification URLs
    path('certifications/', views.certification_list, name='certification_list'),
    path('certifications/<int:pk>/', views.certification_detail, name='certification_detail'),
    path('certifications/create/', views.certification_create, name='certification_create'),
    path('certifications/<int:pk>/update/', views.certification_update, name='certification_update'),
    path('certifications/<int:pk>/delete/', views.certification_delete, name='certification_delete'),
    
    # Meet URLs
    path('meets/', views.meet_list, name='meet_list'),
    path('meets/<int:pk>/', views.meet_detail, name='meet_detail'),
    path('meets/create/', views_meets.meet_create, name='meet_create'),
    path('meets/create/step1/', views_meets.meet_create_step1, name='meet_create_step1'),
    path('meets/create/step2/', views_meets.meet_create_step2, name='meet_create_step2'),
    path('meets/create/step3/', views_meets.meet_create_step3, name='meet_create_step3'),
    path('meets/<int:pk>/update/', views.meet_update, name='meet_update'),
    path('meets/<int:pk>/delete/', views.meet_delete, name='meet_delete'),
    
    # Assignment URLs
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/create/<int:meet_id>/', views.assignment_create, name='assignment_create_for_meet'),
    path('assignments/<int:pk>/update/', views.assignment_update, name='assignment_update'),
    path('assignments/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),
    
    # Event URLs
    path('events/', views_events.EventListView.as_view(), name='event-list'),
    path('events/<int:pk>/', views_events.EventDetailView.as_view(), name='event-detail'),
    path('events/new/', views_events.EventCreateView.as_view(), name='event-create'),
    path('events/<int:pk>/edit/', views_events.EventUpdateView.as_view(), name='event-update'),
    path('events/<int:pk>/delete/', views_events.EventDeleteView.as_view(), name='event-delete'),
    path('events/import/', views_events.EventImportView.as_view(), name='event-import'),
    path('events/delete-all/', views_events.EventDeleteAllView.as_view(), name='event-delete-all'),
    path('events/delete-selected/', views_events.EventDeleteSelectedView.as_view(), name='event-delete-selected'),
    path('events/download-template/', views_events.DownloadEventTemplateView.as_view(), name='event-download-template'),
    
    # Event Position URLs
    path('event-positions/', views_event_positions.EventPositionListView.as_view(), name='event-position-list'),
    path('event-positions/<int:pk>/manage/', views_event_positions.EventPositionManageView.as_view(), name='event-position-manage'),
    path('event-positions/create/', views_event_positions.EventPositionCreateView.as_view(), name='event-position-create'),
    path('event-positions/quick-add/', views_event_positions.EventPositionQuickAddView.as_view(), name='event-position-quick-add'),
    path('event-positions/auto-assign/', views_event_positions.AutoAssignPositionsView.as_view(), name='event-position-auto-assign'),
    path('event-positions/remove-all/', views_event_positions.RemoveAllEventPositionsView.as_view(), name='event-position-remove-all'),

    # API endpoints
    path('api/teams/<int:team_id>/pools/', api_views.team_pools, name='api_team_pools'),
    path('api/divisions/<int:division_id>/teams/', api_views.division_teams, name='api_division_teams'),
    path('api/leagues/<int:league_id>/divisions/', api_views.league_divisions, name='api_league_divisions'),
    path('api/weather/', api_views.weather_forecast, name='api_weather_forecast'),
    path('api/weather/pool/', api_views.pool_weather, name='api_pool_weather'),
    
    # Strategy URLs
    path('strategies/', views_strategy.strategy_list, name='strategy_list'),
    path('strategies/<int:pk>/', views_strategy.strategy_detail, name='strategy_detail'),
    path('strategies/create/', views_strategy.strategy_create, name='strategy_create'),
    path('strategies/<int:pk>/update/', views_strategy.strategy_update, name='strategy_update'),
    path('strategies/<int:pk>/delete/', views_strategy.strategy_delete, name='strategy_delete'),

    # Position URLs
    path('positions/', views_position.PositionListView.as_view(), name='position_list'),
    path('positions/create/', views_position.PositionCreateView.as_view(), name='position_create'),
    path('positions/import/', views_position.PositionImportView.as_view(), name='position_import'),
    path('positions/import/sample/', views_position.download_position_import_template, name='position_import_sample'),
    path('positions/<int:pk>/update/', views_position.PositionUpdateView.as_view(), name='position_update'),
    path('positions/<int:pk>/delete/', views_position.PositionDeleteView.as_view(), name='position_delete'),
]
