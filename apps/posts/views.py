from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import F, Exists, OuterRef
from core.responses import success_response, created_response, no_content_response
from core.permissions import IsOwnerOrReadOnly
from core.pagination import CustomCursorPagination
from .models import Post, Comment, Like, VideoView
from .serializers import PostSerializer, CommentSerializer

class PostListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        serializer = PostSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return created_response(data=serializer.data)

class PostDetailView(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = Post.objects.select_related('user')
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_liked_by_user=Exists(Like.objects.filter(post=OuterRef('pk'), user=self.request.user))
            )
        return qs

    def get(self, request, pk):
        post = get_object_or_404(self.get_queryset(), pk=pk)
        return success_response(data=PostSerializer(post, context={'request': request}).data)

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        post.delete()
        return no_content_response()

    def put(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data)

class PostLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        with transaction.atomic():
            like, created = Like.objects.get_or_create(user=request.user, post=post)
            if created:
                Post.objects.filter(pk=pk).update(like_count=F('like_count') + 1)
                liked = True
            else:
                like.delete()
                Post.objects.filter(pk=pk).update(like_count=F('like_count') - 1)
                liked = False
            
            post.refresh_from_db()
            return success_response(data={"liked": liked, "like_count": post.like_count})

class PostViewCountView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        user = request.user if request.user.is_authenticated else None
        ip_address = request.META.get('REMOTE_ADDR')

        if user:
            # Unique view for authenticated
            view, created = VideoView.objects.get_or_create(post=post, user=user, defaults={'ip_address': ip_address})
            if created:
                Post.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
        else:
            # Anonymous view
            VideoView.objects.create(post=post, user=None, ip_address=ip_address)
            Post.objects.filter(pk=pk).update(view_count=F('view_count') + 1)

        post.refresh_from_db()
        return success_response(data={"view_count": post.view_count})

class PostCommentsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        comments = Comment.objects.filter(post=post).select_related('user').order_by('-created_at')
        
        paginator = CustomCursorPagination()
        page = paginator.paginate_queryset(comments, request, view=self)
        return paginator.get_paginated_response(CommentSerializer(page, many=True).data)

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            comment = serializer.save(user=request.user, post=post)
            Post.objects.filter(pk=pk).update(comment_count=F('comment_count') + 1)
            
        return created_response(data=CommentSerializer(comment).data)

class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk, post_id=pk)
        if comment.user != request.user:
            self.permission_denied(request, message="Not owner")
            
        with transaction.atomic():
            comment.delete()
            Post.objects.filter(pk=pk).update(comment_count=F('comment_count') - 1)
            
        return no_content_response()

class PostForkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        original_post = get_object_or_404(Post, pk=pk, post_type='snippet')
        
        # Fork attributes from request or default to original
        # Request could have modified 'code', 'content', 'language'
        new_code = request.data.get('code', original_post.code)
        new_content = request.data.get('content', original_post.content)
        new_language = request.data.get('language', original_post.language)
        
        with transaction.atomic():
            new_post = Post.objects.create(
                user=request.user,
                post_type='snippet',
                content=new_content,
                code=new_code,
                language=new_language,
                forked_from=original_post
            )
            Post.objects.filter(pk=pk).update(fork_count=F('fork_count') + 1)
            
        return created_response(data=PostSerializer(new_post, context={'request': request}).data)
