from django.urls import path
from .views import (
    CurrentUserView, AvatarUploadView, UserSearchView,
    UserProfileView, FollowView, FollowersListView,
    FollowingListView, UserPostsListView
)
from apps.repos.views import UserReposListView

urlpatterns = [
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('me/avatar/', AvatarUploadView.as_view(), name='upload_avatar'),
    path('search/', UserSearchView.as_view(), name='search_users'),
    path('<str:username>/', UserProfileView.as_view(), name='user_profile'),
    path('<str:username>/follow/', FollowView.as_view(), name='follow_user'),
    path('<str:username>/followers/', FollowersListView.as_view(), name='followers_list'),
    path('<str:username>/following/', FollowingListView.as_view(), name='following_list'),
    path('<str:username>/posts/', UserPostsListView.as_view(), name='user_posts'),
    path('<str:username>/repos/', UserReposListView.as_view(), name='user_repos'),
]
