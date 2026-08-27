from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.db.models import F
from django.contrib.auth import get_user_model
from core.responses import success_response, created_response, no_content_response
from core.storage import upload_repo_file
from .models import Repository, RepoFile
from .serializers import RepositorySerializer, RepoFileSerializer

User = get_user_model()

class RepositoryListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        cursor = request.query_params.get('cursor')
        limit = 10
        qs = Repository.objects.filter(visibility='public').order_by('-created_at')
        
        if cursor:
            try:
                # Basic cursor pagination assuming cursor is a created_at string
                from django.utils.dateparse import parse_datetime
                cursor_date = parse_datetime(cursor)
                if cursor_date:
                    qs = qs.filter(created_at__lt=cursor_date)
            except:
                pass
                
        repos = list(qs[:limit + 1])
        has_next = len(repos) > limit
        repos = repos[:limit]
        
        next_cursor = None
        if has_next and repos:
            next_cursor = repos[-1].created_at.isoformat()
            
        return success_response(data={
            'results': RepositorySerializer(repos, many=True).data,
            'next_cursor': next_cursor
        })

    def post(self, request):
        serializer = RepositorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        repo = serializer.save(user=request.user)
        return created_response(data=RepositorySerializer(repo).data)

class UserReposListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        # Assuming only public repos for public endpoints, unless it's own profile (handled on client or expanded logic here)
        qs = Repository.objects.filter(user=user, visibility='public').order_by('-created_at')
        return success_response(data=RepositorySerializer(qs, many=True).data)

class RepositoryDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username, repo_name):
        user = get_object_or_404(User, username=username)
        repo = get_object_or_404(Repository, user=user, name=repo_name)
        
        if repo.visibility == 'private' and request.user != user:
            self.permission_denied(request, message="Repository is private")
            
        return success_response(data=RepositorySerializer(repo).data)

class RepositoryDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        repo = get_object_or_404(Repository, pk=pk, user=request.user)
        repo.delete()
        return no_content_response()

class RepoFileListView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        repo = get_object_or_404(Repository, pk=pk, user=request.user)
        file = request.FILES.get('file')
        if not file:
            return success_response(message="File is required", status_code=400)
            
        if file.size > 50 * 1024 * 1024:
            return success_response(message="Max file size is 50MB", status_code=400)

        file_url = upload_repo_file(file)
        
        repo_file = RepoFile.objects.create(
            repo=repo,
            filename=file.name,
            file_url=file_url,
            file_size=file.size,
            file_type=file.content_type or 'application/octet-stream'
        )
        
        return created_response(data=RepoFileSerializer(repo_file).data)

class RepoFileDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, file_id):
        repo = get_object_or_404(Repository, pk=pk, user=request.user)
        repo_file = get_object_or_404(RepoFile, pk=file_id, repo=repo)
        repo_file.delete()
        return no_content_response()

class RepoFileDownloadView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk, file_id):
        repo = get_object_or_404(Repository, pk=pk)
        
        if repo.visibility == 'private' and request.user != repo.user:
            self.permission_denied(request, message="Repository is private")
            
        repo_file = get_object_or_404(RepoFile, pk=file_id, repo=repo)
        
        # update download count
        with transaction.atomic():
            Repository.objects.filter(pk=pk).update(download_count=F('download_count') + 1)
            
        return redirect(repo_file.file_url)
