from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated

class IsAuthenticatedAndRequires401(BasePermission):
    """Custom permission to require authentication and return 401 instead of 403."""
    
    def has_permission(self, request, view):
        # Check if request has been marked as a regular Django view by middleware
        is_regular_django_view = getattr(request, 'is_regular_django_view', False)
        
        # If middleware has flagged this as a regular Django view, always return True
        # to let Django's authentication middleware handle it
        if is_regular_django_view:
            return True
            
        # Get path info to determine if this is an API request vs regular web request
        path_info = getattr(request, 'path_info', '')
        
        # Check if this is an API path (starts with '/api/')
        is_api_path = path_info.startswith('/api/')
        
        # Secondary check - if the HTTP_ACCEPT header specifically requests JSON/XML
        accept_header = request.META.get('HTTP_ACCEPT', '')
        wants_api_format = 'application/json' in accept_header or 'application/xml' in accept_header
        wants_html = 'text/html' in accept_header
        
        # If authenticated, always allow
        if request.user and request.user.is_authenticated:
            return True
