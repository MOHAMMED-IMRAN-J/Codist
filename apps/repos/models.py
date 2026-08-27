import uuid
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Repository(models.Model):
    VISIBILITY_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repositories')
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True, null=True)
    languages = models.CharField(max_length=255, blank=True, null=True, help_text="Comma separated languages")
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    
    download_count = models.IntegerField(default=0)
    star_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'name')
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['visibility']),
        ]

    def __str__(self):
        return f"{self.user.username}/{self.name}"

class RepoFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='files')
    filename = models.CharField(max_length=255)
    file_url = models.URLField(max_length=500)
    file_size = models.IntegerField(help_text="bytes")
    file_type = models.CharField(max_length=50)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['repo']),
        ]

    def __str__(self):
        return f"{self.repo.name}/{self.filename}"
