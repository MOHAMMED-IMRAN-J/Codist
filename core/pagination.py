from rest_framework.pagination import CursorPagination
from rest_framework.response import Response

class CustomCursorPagination(CursorPagination):
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 50
    ordering = '-created_at'
    
    def get_paginated_response(self, data):
        return Response({
            'data': {
                'results': data,
                'next_cursor': self.get_next_link(),
                'previous_cursor': self.get_previous_link()
            },
            'message': 'ok'
        })
