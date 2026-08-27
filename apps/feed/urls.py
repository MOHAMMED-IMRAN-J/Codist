from django.urls import path
from .views import FeedView, ExploreView

urlpatterns = [
    path('', FeedView.as_view(), name='feed_personalized'),
    path('explore/', ExploreView.as_view(), name='feed_explore'),
]
