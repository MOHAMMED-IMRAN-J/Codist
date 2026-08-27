from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'bio', 'avatar_url', 'github_url',
            'follower_count', 'following_count', 'post_count',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'follower_count', 'following_count', 'post_count',
            'is_active', 'created_at', 'updated_at'
        ]

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['bio', 'avatar_url', 'github_url']
