from rest_framework import serializers
from .models import Repository, RepoFile

class RepoFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepoFile
        fields = ['id', 'filename', 'file_url', 'file_size', 'file_type', 'uploaded_at']

class RepositorySerializer(serializers.ModelSerializer):
    files = RepoFileSerializer(many=True, read_only=True)
    
    class Meta:
        model = Repository
        fields = ['id', 'user', 'name', 'description', 'languages', 'visibility', 'download_count', 'star_count', 'created_at', 'updated_at', 'files']
        read_only_fields = ['id', 'user', 'download_count', 'star_count', 'created_at', 'updated_at']
