from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from core.responses import success_response
from .languages import LANGUAGES
from .services import execute_code

class LanguagesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return success_response(data=LANGUAGES)

class ExecuteCodeView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key='user', rate='10/m', method='POST', block=True))
    def post(self, request):
        source_code = request.data.get('source_code')
        language_id = request.data.get('language_id')
        stdin = request.data.get('stdin', '')

        if not source_code or not language_id:
            return success_response(message="source_code and language_id are required", status_code=400)

        if len(source_code) > 50000:
            return success_response(message="Source code exceeds maximum length of 50000 characters", status_code=400)

        result = execute_code(source_code, language_id, stdin)
        return success_response(data=result)
