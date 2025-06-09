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
    try:
        team = Team.objects.get(id=team_id)
        pools = Pool.objects.filter(team=team)
        data = [{
            'id': pool.id,
            'name': pool.name,
            'address': pool.address,
            'length': pool.length,
            'units': pool.units,
            'lanes': pool.lanes,
            'bidirectional': pool.bidirectional,
        } for pool in pools]
        return JsonResponse(data, safe=False)
    except Team.DoesNotExist:
        return JsonResponse([], safe=False)


def division_teams(request, division_id):
    """API endpoint to get all teams in a specific division."""
    try:
        division = Division.objects.get(id=division_id)
        teams = Team.objects.filter(division=division)
        data = [{
            'id': team.id,
            'name': team.name,
        } for team in teams]
        return JsonResponse(data, safe=False)
    except Division.DoesNotExist:
        return JsonResponse([], safe=False)
        

def league_divisions(request, league_id):
    """API endpoint to get all divisions in a specific league."""
    try:
        league = League.objects.get(id=league_id)
        divisions = Division.objects.filter(league=league)
        data = [{
            'id': division.id,
            'name': division.name,
        } for division in divisions]
        return JsonResponse(data, safe=False)
    except League.DoesNotExist:
        return JsonResponse([], safe=False)


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


def pool_weather(request):
    """API endpoint to get weather forecast for a specific pool."""
    pool_id = request.GET.get('pool_id', '')
    
    if not pool_id:
        return JsonResponse({'error': 'Pool ID is required'})
    
    try:
        # Get the pool by its ID - use direct query instead of get_object_or_404
        try:
            pool = Pool.objects.get(id=pool_id)
            address = pool.address if hasattr(pool, 'address') else 'Unknown location'
        except Pool.DoesNotExist:
            return JsonResponse({'error': 'Pool not found'})
        
        # Use current date instead of trying to access session
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Simulated weather data (always returns success for demo purposes)
        # Current weather
        current_weather = {
            'temp': 78,
            'description': 'Sunny',
            'icon_url': 'https://openweathermap.org/img/wn/01d@2x.png',
            'wind_speed': 5
        }
        
        # Forecast for meet day
        forecast_weather = {
            'min_temp': 68,
            'max_temp': 82,
            'description': 'Clear skies',
            'icon_url': 'https://openweathermap.org/img/wn/01d@2x.png',
            'pop': 10  # Probability of precipitation
        }
        
        return JsonResponse({
            'current': current_weather,
            'forecast': forecast_weather,
            'location': address,
            'date': current_date
        })
        
    except Exception as e:
        # Log the exception for debugging but return a generic message
        # print(f"Weather API error: {str(e)}") # Uncomment for debugging
        return JsonResponse({
            # Return mock data even in case of error for demo purposes
            'current': {
                'temp': 75,
                'description': 'Partly Cloudy',
                'icon_url': 'https://openweathermap.org/img/wn/02d@2x.png',
                'wind_speed': 7
            },
            'forecast': {
                'min_temp': 65,
                'max_temp': 80,
                'description': 'Variable conditions',
                'icon_url': 'https://openweathermap.org/img/wn/03d@2x.png',
                'pop': 30
            },
            'location': 'Default location',
            'date': datetime.now().strftime('%Y-%m-%d')
        })



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

