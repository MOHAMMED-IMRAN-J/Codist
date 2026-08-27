from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.cache import cache
from celery.result import AsyncResult
from core.responses import success_response
from core.storage import upload_image, upload_video_async
from apps.posts.tasks import upload_video_task

class ImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('image')
        if not file:
            return success_response(message="Image file required", status_code=400)
            
        if file.size > 10 * 1024 * 1024:
            return success_response(message="Max file size is 10MB", status_code=400)
            
        image_url = upload_image(file)
        return success_response(data={"image_url": image_url})

class DirectVideoUploadView(APIView):
    """Synchronous video upload — no Celery needed."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        # Debug: log what's arriving
        print("=== VIDEO UPLOAD DEBUG ===")
        print(f"Content-Type: {request.content_type}")
        print(f"FILES keys: {list(request.FILES.keys())}")
        print(f"FILES values: {request.FILES}")
        print(f"DATA keys: {list(request.data.keys())}")
        print(f"DATA: {request.data}")
        print("=========================")
        
        # Try multiple field names since React Native FormData can vary
        file = request.FILES.get('video') or request.FILES.get('file') or request.FILES.get('image')
        
        # Fallback: grab the first file from FILES regardless of field name
        if not file and request.FILES:
            file = list(request.FILES.values())[0]

        if not file:
            return success_response(message="Video file required", status_code=400)

        if file.size > 100 * 1024 * 1024:
            return success_response(message="Max file size is 100MB", status_code=400)

        result = upload_video_async(file)
        return success_response(data=result)

class VideoUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('video')
        if not file:
            return success_response(message="Video file required", status_code=400)
            
        if file.size > 100 * 1024 * 1024:
            return success_response(message="Max file size is 100MB", status_code=400)
            
        # Read file to bytes to pass to Celery
        file_bytes = file.read()
        task = upload_video_task.delay(file_bytes, file.name)
        
        return success_response(data={"task_id": task.id})

class VideoUploadStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        res = AsyncResult(task_id)
        if res.ready():
            if res.successful():
                data = res.result
                return success_response(data=data)
            else:
                return success_response(data={"status": "failed"}, status_code=500)
        
        return success_response(data={"status": "pending"})
