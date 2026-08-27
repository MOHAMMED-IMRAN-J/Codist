from django.urls import path
from .views import (
    RepositoryListCreateView, UserReposListView,
    RepositoryDetailView, RepositoryDeleteView,
    RepoFileListView, RepoFileDeleteView, RepoFileDownloadView
)

urlpatterns = [
    path('', RepositoryListCreateView.as_view(), name='repo_list_create'),
    path('<uuid:pk>/', RepositoryDeleteView.as_view(), name='repo_delete'),
    path('<uuid:pk>/files/', RepoFileListView.as_view(), name='repo_files'),
    path('<uuid:pk>/files/<uuid:file_id>/', RepoFileDeleteView.as_view(), name='repo_file_delete'),
    path('<uuid:pk>/files/<uuid:file_id>/download/', RepoFileDownloadView.as_view(), name='repo_file_download'),
    path('<str:username>/<str:repo_name>/', RepositoryDetailView.as_view(), name='repo_detail_by_name'),
    # Note: the user profile list is usually in users API, but requirement said:
    # GET /api/v1/users/{username}/repos/ -> handled centrally in app.repos, but let's map it under users via users.urls or map it here.
    # The requirement strictly states the URIs. Let's make sure they match.
]

# We should add a separate urls block for the ones matching /api/v1/users/x/repos
# Or we can put it here and include it using a different router block in codist/urls.py
