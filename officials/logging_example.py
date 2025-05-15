import logging

# Get a logger for this module
logger = logging.getLogger('officials')

def log_example():
    """Example function demonstrating different log levels"""
    logger.debug('This is a debug message - only visible when DEBUG=True')
    logger.info('This is an info message - always logged to file')
    logger.warning('This is a warning message - something to pay attention to')
    logger.error('This is an error message - something went wrong')
    logger.critical('This is a critical message - serious problem detected')

# Example of how to use logging in views
def example_view(request):
    try:
        # Log the request
        logger.info(f'Received request from {request.user} to access example view')
        
        # Your view logic here
        result = perform_some_operation()
        
        # Log successful operation
        logger.info(f'Successfully processed request for {request.user}')
        
        return result
    except Exception as e:
        # Log any exceptions that occur
        logger.error(f'Error in example_view: {str(e)}', exc_info=True)
        # Re-raise or handle the exception as needed
        raise

def perform_some_operation():
    # Log at the start of an operation
    logger.info('Starting operation')
    
    # Sometimes you want to log detailed information only in debug mode
    logger.debug('Detailed debugging information')
    
    # Log warnings for potential issues
    if some_condition:
        logger.warning('Potential issue detected: condition is True')
    
    # Log the completion of the operation
    logger.info('Operation completed successfully')
    
    return result
