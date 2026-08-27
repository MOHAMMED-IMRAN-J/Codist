from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Exists, OuterRef
from apps.posts.models import Post, Like
from apps.users.models import Follow
from apps.posts.serializers import PostSerializer
from core.pagination import CustomCursorPagination

class FeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # User requested to see all posts from all users in the feed tab
        qs = Post.objects.select_related('user').order_by('-created_at')
        
        # Annotate with whether the current user liked it
        qs = qs.annotate(
            is_liked_by_user=Exists(Like.objects.filter(post=OuterRef('pk'), user=request.user))
        )
        
        paginator = CustomCursorPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        
        return paginator.get_paginated_response(PostSerializer(page, many=True, context={'request': request}).data)

class ExploreView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Post.objects.select_related('user').order_by('-like_count', '-created_at')
        
        post_type = request.query_params.get('type')
        if post_type:
            qs = qs.filter(post_type=post_type)
            
        if request.user.is_authenticated:
            qs = qs.annotate(
                is_liked_by_user=Exists(Like.objects.filter(post=OuterRef('pk'), user=request.user))
            )
            
        paginator = CustomCursorPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        
        return paginator.get_paginated_response(PostSerializer(page, many=True, context={'request': request}).data)
