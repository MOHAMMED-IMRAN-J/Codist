from django.urls import path
from .views import (
    PostListCreateView, PostDetailView, PostLikeView,
    PostViewCountView, PostCommentsView, CommentDeleteView,
    PostForkView
)
from .upload_views import ImageUploadView, VideoUploadView, VideoUploadStatusView, DirectVideoUploadView

urlpatterns = [
    path('upload/image/', ImageUploadView.as_view(), name='upload_image'),
    path('upload/video/direct/', DirectVideoUploadView.as_view(), name='upload_video_direct'),
    path('upload/video/', VideoUploadView.as_view(), name='upload_video'),
    path('upload/video/<str:task_id>/status/', VideoUploadStatusView.as_view(), name='upload_video_status'),
    path('', PostListCreateView.as_view(), name='post_list_create'),
    path('<uuid:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('<uuid:pk>/like/', PostLikeView.as_view(), name='post_like'),
    path('<uuid:pk>/view/', PostViewCountView.as_view(), name='post_view'),
    path('<uuid:pk>/comments/', PostCommentsView.as_view(), name='post_comments'),
    path('<uuid:pk>/comments/<uuid:comment_pk>/', CommentDeleteView.as_view(), name='comment_delete'),
    path('<uuid:pk>/fork/', PostForkView.as_view(), name='post_fork'),
]
