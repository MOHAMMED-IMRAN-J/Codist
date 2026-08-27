from rest_framework import serializers
from .models import Post, Comment, Like, VideoView
from apps.users.serializers import UserSerializer

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'user', 'post_type', 'title', 'content', 'code', 'language',
            'category', 'description',
            'media_url', 'video_url', 'thumbnail_url', 'duration',
            'like_count', 'comment_count', 'fork_count', 'view_count',
            'forked_from', 'created_at', 'updated_at', 'is_liked'
        ]
        read_only_fields = [
            'id', 'like_count', 'comment_count', 'fork_count', 'view_count',
            'created_at', 'updated_at'
        ]

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Optimize to avoid N+1 if we prefetch liked IDs or use getattr
            if hasattr(obj, 'is_liked_by_user'):
                return obj.is_liked_by_user
            # Fallback
            return Like.objects.filter(post=obj, user=request.user).exists()
        return False

    def validate(self, attrs):
        post_type = attrs.get('post_type')
        if post_type == 'snippet':
            if not attrs.get('code'):
                raise serializers.ValidationError("Code is required for snippet posts.")
            if not attrs.get('language'):
                raise serializers.ValidationError("Language is required for snippet posts.")
        elif post_type == 'video':
            if not attrs.get('video_url'):
                raise serializers.ValidationError("Video URL is required for video posts.")
        elif post_type == 'blog':
            if not attrs.get('title'):
                raise serializers.ValidationError("Title is required for blog posts.")
        return attrs
