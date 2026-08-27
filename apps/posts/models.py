import uuid
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Post(models.Model):
    POST_TYPES = (
        ('post', 'Post'),
        ('snippet', 'Snippet'),
        ('video', 'Video'),
        ('blog', 'Blog'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=20, choices=POST_TYPES)
    
    title = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    code = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    media_url = models.URLField(max_length=500, blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True, null=True)
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    fork_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    
    forked_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='forks')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['post_type']),
            models.Index(fields=['language']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['-like_count']),
        ]

    def __str__(self):
        return f"{self.post_type} by {self.user}"

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]

class Like(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

class VideoView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='video_views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='video_views')
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
