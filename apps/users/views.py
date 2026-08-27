from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from core.responses import success_response
from core.storage import upload_image
from .serializers import UserSerializer, UserProfileUpdateSerializer
from .models import Follow
from core.pagination import CustomCursorPagination

User = get_user_model()

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(data=UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=UserSerializer(request.user).data)

class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('avatar')
        if not file:
            return success_response(message="Avatar field is required", status_code=400)
        
        avatar_url = upload_image(file)
        request.user.avatar_url = avatar_url
        request.user.save(update_fields=['avatar_url'])
        
        return success_response(data={"avatar_url": avatar_url})

class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return success_response(data=[])
        users = User.objects.filter(Q(username__icontains=query) | Q(email__icontains=query))[:20]
        return success_response(data=UserSerializer(users, many=True).data)

class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        data = UserSerializer(user).data
        
        if request.user.is_authenticated:
            data['is_following'] = Follow.objects.filter(follower=request.user, following=user).exists()
            
        return success_response(data=data)

class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        target_user = get_object_or_404(User, username=username)
        
        if request.user == target_user:
            return success_response(message="Cannot follow yourself", status_code=400)

        with transaction.atomic():
            follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
            
            if hasattr(self, '_run_counter_update_if_needed'):
                pass  # Internal usage optimization comment

            if created:
                User.objects.filter(id=request.user.id).update(following_count=F('following_count') + 1)
                User.objects.filter(id=target_user.id).update(follower_count=F('follower_count') + 1)
                following = True
            else:
                follow.delete()
                User.objects.filter(id=request.user.id).update(following_count=F('following_count') - 1)
                User.objects.filter(id=target_user.id).update(follower_count=F('follower_count') - 1)
                following = False
            
            # Refresh from db to get new counts
            target_user.refresh_from_db()
            
            return success_response(data={
                "following": following,
                "follower_count": target_user.follower_count
            })

class FollowersListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        follows = Follow.objects.filter(following=user).select_related('follower')
        paginator = CustomCursorPagination()
        page = paginator.paginate_queryset(follows, request, view=self)
        users = [f.follower for f in page]
        return paginator.get_paginated_response(UserSerializer(users, many=True).data)

class FollowingListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        follows = Follow.objects.filter(follower=user).select_related('following')
        paginator = CustomCursorPagination()
        page = paginator.paginate_queryset(follows, request, view=self)
        users = [f.following for f in page]
        return paginator.get_paginated_response(UserSerializer(users, many=True).data)

class UserPostsListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        from apps.posts.models import Post
        from apps.posts.serializers import PostSerializer
        
        qs = Post.objects.filter(user=user).select_related('user').order_by('-created_at')
        
        post_type = request.query_params.get('type')
        if post_type:
            qs = qs.filter(post_type=post_type)
            
        paginator = CustomCursorPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        
        # We need to inject user authentication state for 'is_liked' to PostSerializer
        context = {'request': request}
        
        return paginator.get_paginated_response(PostSerializer(page, many=True, context=context).data)
