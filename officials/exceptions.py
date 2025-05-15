from rest_framework.views import APIView
from rest_framework.views import exception_handler as drf_exception_handler
import logging

logger = logging.getLogger(__name__)

# Consistent API path prefix with negotiation.py
API_PATH_PREFIX = '/api/'

def custom_exception_handler(exc, context):
    request = context.get('request')
    view = context.get('view')
    
    # Check if this is an API request based on path prefix
    path = request.path if request else 'N/A'
    is_api_path = path.startswith(API_PATH_PREFIX) if path != 'N/A' else False
    
    # Also check if it's an API view (both checks ensure we don't miss anything)
    is_api_view_check = view and isinstance(view, APIView)
    
    # Combined check - treat as API if either condition is true
    is_api_request = is_api_path or is_api_view_check
    
    logger.info(
        f"CustomExceptionHandler: Exception '{type(exc).__name__}' in view "
        f"'{type(view).__name__ if view else 'None'}' (path: {path}). "
        f"Is API path: {is_api_path}, Is APIView: {is_api_view_check}, Handling as API: {is_api_request}"
    )

    if is_api_request:
        # This is an API request, so let DRF handle it
        return drf_exception_handler(exc, context)
    else:
        # For Django views, return None so Django's middleware handles it
        return None
