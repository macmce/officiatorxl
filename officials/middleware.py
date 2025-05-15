"""
Custom middleware for officials app.
"""
from django.urls import resolve

class DisableDRFForRegularViewsMiddleware:
    """
    Middleware that prevents Django REST Framework from handling regular Django views.
    This is needed because DRF sometimes interferes with regular Django views and renders
    API templates instead of regular Django templates.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check if this is an API path
        path_info = request.path_info
        
        # Mark non-API paths to prevent DRF from handling them
        if not path_info.startswith('/api/'):
            # Add a flag to the request that can be checked in content negotiation
            request.is_regular_django_view = True
            
            # For tests that use assertTemplateUsed, make sure we're not using DRF renderers
            if 'HTTP_ACCEPT' not in request.META:
                request.META['HTTP_ACCEPT'] = 'text/html'
        
        response = self.get_response(request)
        return response
