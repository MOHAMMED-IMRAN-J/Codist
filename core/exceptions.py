from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            'error': response.data.get('detail', 'An error occurred') if isinstance(response.data, dict) else str(response.data),
            'code': getattr(exc, 'default_code', 'error').upper(),
            'details': response.data if isinstance(response.data, dict) and 'detail' not in response.data else {}
        }
        
        # DRF fields validation errors usually appear as lists/dicts mapping field names to errors
        if isinstance(response.data, dict) and 'detail' not in response.data:
            custom_data['error'] = 'Validation Error'
            custom_data['code'] = 'VALIDATION_ERROR'

        response.data = custom_data

    return response
