from rest_framework.response import Response
from rest_framework import status

def success_response(data=None, message="ok", status_code=status.HTTP_200_OK):
    return Response({
        "data": data if data is not None else {},
        "message": message
    }, status=status_code)

def created_response(data=None, message="created"):
    return success_response(data, message, status.HTTP_201_CREATED)

def no_content_response():
    return Response(status=status.HTTP_204_NO_CONTENT)
