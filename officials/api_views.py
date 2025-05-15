from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import (Team, Pool, League, Certification, Division, Official, Meet, 
                    Assignment, Event, Strategy, Position, UserLeagueAdmin)
from .serializers import (LeagueSerializer, CertificationSerializer, DivisionSerializer, TeamSerializer, 
                        OfficialSerializer, MeetSerializer, PoolSerializer, AssignmentSerializer, 
                        EventSerializer, StrategySerializer, PositionSerializer, UserLeagueAdminSerializer)
from rest_framework import viewsets, permissions
import requests
import json
from datetime import datetime

def team_pools(request, team_id):
    """API endpoint to get all pools for a specific team."""
    team = get_object_or_404(Team, id=team_id)
    pools = team.pools.all()
    
    pools_data = []
    for pool in pools:
        pools_data.append({
            'id': pool.id,
            'name': pool.name,
            'address': pool.address,
            'length': pool.length,
            'units': pool.units,
            'lanes': pool.lanes,
            'bidirectional': pool.bidirectional
        })
    
    return JsonResponse(pools_data, safe=False)

def weather_forecast(request):
    """API endpoint to get weather forecast for a specific address and date."""
    address = request.GET.get('address', '')
    date_str = request.GET.get('date', '')
    
    if not address or not date_str:
        return JsonResponse({'error': 'Address and date are required'})
    
    try:
        # Parse the date
        forecast_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # For a real implementation, you would use a weather API like OpenWeatherMap
        # Here's a simulated response for demonstration purposes
        
        # In a real application, uncomment this code and use your API key
        # api_key = 'your_openweathermap_api_key'
        # geo_url = f'http://api.openweathermap.org/geo/1.0/direct?q={address}&limit=1&appid={api_key}'
        # geo_response = requests.get(geo_url)
        # geo_data = geo_response.json()
        # 
        # if not geo_data:
        #     return JsonResponse({'error': 'Could not find location'})
        # 
        # lat = geo_data[0]['lat']
        # lon = geo_data[0]['lon']
        # 
        # weather_url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=imperial&appid={api_key}'
        # weather_response = requests.get(weather_url)
        # weather_data = weather_response.json()
        
        # Simulated weather data
        weather_data = {
            'temperature': 75,
            'description': 'Partly Cloudy',
            'precipitation': 20,
            'humidity': 65,
            'wind': 8,
            'units': 'imperial',
            'forecast_date': forecast_date.strftime('%Y-%m-%d')
        }
        
        return JsonResponse(weather_data)
        
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'})
    except Exception as e:
        return JsonResponse({'error': f'Error fetching weather: {str(e)}'})


class LeagueViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows leagues to be viewed or edited.
    """
    queryset = League.objects.all().order_by('name')
    serializer_class = LeagueSerializer
    permission_classes = [permissions.IsAuthenticated]


class CertificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows certifications to be viewed or edited.
    """
    queryset = Certification.objects.all().order_by('name')
    serializer_class = CertificationSerializer
    permission_classes = [permissions.IsAuthenticated]


class DivisionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows divisions to be viewed or edited.
    """
    queryset = Division.objects.all().order_by('league__name', 'name')
    serializer_class = DivisionSerializer
    permission_classes = [permissions.IsAuthenticated]


class TeamViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows teams to be viewed or edited.
    """
    queryset = Team.objects.all().order_by('division__league__name', 'division__name', 'name')
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]


class OfficialViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows officials to be viewed or edited.
    """
    queryset = Official.objects.all().order_by('name')
    serializer_class = OfficialSerializer
    permission_classes = [permissions.IsAuthenticated]


class MeetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows meets to be viewed or edited.
    """
    queryset = Meet.objects.all().order_by('-date', 'name') # Order by date descending, then name
    serializer_class = MeetSerializer
    permission_classes = [permissions.IsAuthenticated]


class PoolViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows pools to be viewed or edited.
    """
    queryset = Pool.objects.all().order_by('name')
    serializer_class = PoolSerializer
    permission_classes = [permissions.IsAuthenticated]


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows assignments to be viewed or edited.
    """
    queryset = Assignment.objects.all().order_by('-meet__date', 'official__name')
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows events to be viewed or edited.
    """
    queryset = Event.objects.all().order_by('event_number')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]


class StrategyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows strategies to be viewed or edited.
    """
    queryset = Strategy.objects.all().order_by('name')
    serializer_class = StrategySerializer
    permission_classes = [permissions.IsAuthenticated]


class PositionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows positions to be viewed or edited.
    """
    queryset = Position.objects.all().order_by('strategy__name', 'role')
    serializer_class = PositionSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserLeagueAdminViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user league admin relationships to be viewed or edited.
    """
    queryset = UserLeagueAdmin.objects.all().order_by('user__username', 'league__name')
    serializer_class = UserLeagueAdminSerializer
    permission_classes = [permissions.IsAuthenticated]

