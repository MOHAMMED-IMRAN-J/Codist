from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.auth_urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/posts/', include('apps.posts.urls')),
    path('api/v1/feed/', include('apps.feed.urls')),
    path('api/v1/code/', include('apps.code_runner.urls')),
    path('api/v1/repos/', include('apps.repos.urls')),
    path('api/v1/chat/', include('apps.chat.urls')),
]
