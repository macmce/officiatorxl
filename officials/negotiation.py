from rest_framework.negotiation import DefaultContentNegotiation
from rest_framework.exceptions import NotAcceptable
# DO NOT import APIView at module level to avoid circular imports
import logging

logger = logging.getLogger(__name__)

# Define the API path prefix
API_PATH_PREFIX = '/api/'

class SelectiveContentNegotiation(DefaultContentNegotiation):
    def select_renderer(self, request, renderers, format_suffix):
        # APIView import moved inside the method for type checking if view object exists
        from rest_framework.views import APIView 
        
        view = getattr(request, 'view', None)
        path_info = getattr(request, 'path_info', 'N/A')

        # Check if the request has been marked as a regular Django view by our middleware
        is_regular_django_view = getattr(request, 'is_regular_django_view', False)
        
        # If middleware has marked this as a regular Django view, bypass DRF handling
        if is_regular_django_view:
            logger.info(f"SelectiveContentNegotiation: Request marked as regular Django view for path '{path_info}'")
            return None
            
        # Primary check: Determine if it's an API request based on path prefix
        is_api_path = path_info.startswith(API_PATH_PREFIX) 
        
        # Secondary check - if the HTTP_ACCEPT header specifically requests JSON/XML
        accept_header = request.META.get('HTTP_ACCEPT', '')
        wants_api_format = 'application/json' in accept_header or 'application/xml' in accept_header
        wants_html = 'text/html' in accept_header
        
        # Explicit preference for HTML should override API format checks for non-API paths
        if not is_api_path and wants_html:
            logger.info(f"SelectiveContentNegotiation: HTML requested for non-API path '{path_info}', bypassing DRF")
            return None
        
        # Check if it's an instance of APIView
        is_api_view_instance = view and isinstance(view, APIView)

        logger.info(
            f"SelectiveContentNegotiation.select_renderer for path '{path_info}'. "
            f"View type: '{type(view).__name__ if view else 'None'}'. "
            f"Path starts with '{API_PATH_PREFIX}': {is_api_path}. "
            f"Is APIView instance: {is_api_view_instance}. "
            f"Wants HTML: {wants_html}."
        )

        # Only use DRF rendering for API paths or explicit API requests
        if is_api_path or (wants_api_format and not wants_html):
            # Use DRF's default negotiation
            selected_renderer_tuple = super().select_renderer(request, renderers, format_suffix)
            renderer_name = type(selected_renderer_tuple[0]).__name__ if selected_renderer_tuple and selected_renderer_tuple[0] else 'None'
            media_type = selected_renderer_tuple[1] if selected_renderer_tuple and len(selected_renderer_tuple) > 1 else 'N/A'
            logger.info(
                f"SelectiveContentNegotiation.select_renderer: API path '{path_info}' - "
                f"DRF selected renderer: {renderer_name}, media_type: {media_type}."
            )
            return selected_renderer_tuple
        else:
            # For non-API paths, bypass DRF rendering completely
            logger.info(
                f"SelectiveContentNegotiation.select_renderer: Non-API path '{path_info}' - "
                f"View type: '{type(view).__name__ if view else 'None'}'. Bypassing DRF rendering."
            )
            # Return None to tell DRF not to handle this response
            return None

    def select_parser(self, request, parsers):
        # Import moved inside to avoid circular imports
        from rest_framework.views import APIView
        
        # Check if the request has been marked as a regular Django view by our middleware
        is_regular_django_view = getattr(request, 'is_regular_django_view', False)
        
        view = getattr(request, 'view', None)
        path_info = getattr(request, 'path_info', 'N/A')
        
        # If middleware has marked this as a regular Django view, bypass DRF handling
        if is_regular_django_view:
            logger.info(f"SelectiveContentNegotiation.select_parser: Request marked as regular Django view for path '{path_info}'")
            return None
            
        # Check if this is an API path
        is_api_path = path_info.startswith(API_PATH_PREFIX)
        
        # Secondary check - if the HTTP_ACCEPT header specifically requests JSON/XML
        accept_header = request.META.get('HTTP_ACCEPT', '')
        wants_html = 'text/html' in accept_header
        
        # Explicit preference for HTML should override API format checks for non-API paths
        if not is_api_path and wants_html:
            logger.info(f"SelectiveContentNegotiation.select_parser: HTML requested for non-API path '{path_info}', bypassing DRF")
            return None
            
        # Determine if view is an instance of APIView
        is_api_view = isinstance(view, APIView) if view else None
        
        logger.info(f"SelectiveContentNegotiation.select_parser for view '{type(view).__name__ if view else 'None'}' "
                   f"(path: {path_info}). Is APIView: {is_api_view}.")
        
        # For non-API paths, don't use DRF parsers
        if not is_api_path:
            logger.info(f"SelectiveContentNegotiation.select_parser: Non-API path '{path_info}' - bypassing DRF parsing")
            return None
            
        # If a regular Django view, not a DRF APIView, return a default parser
        if not is_api_view:
            logger.info(f"SelectiveContentNegotiation.select_parser: Non-APIView or no view '{type(view).__name__ if view else 'None'}' - "
                        f"DRF selected parser: JSONParser.")
            # Use a default parser even for non-API views, to avoid errors if some middleware tries to parse the body
            # Get first parser (likely JSONParser) to avoid random exceptions
            return parsers[0] if parsers else None

        # For API views, use DRF's default parser selection
        selected_parser = super().select_parser(request, parsers)
        parser_name = type(selected_parser).__name__ if selected_parser else "None"
        logger.info(f"SelectiveContentNegotiation.select_parser: APIView '{type(view).__name__ if view else 'None'}' - "
                    f"DRF selected parser: {parser_name}.")
        return selected_parser
