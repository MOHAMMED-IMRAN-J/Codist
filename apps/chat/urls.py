from django.urls import path
from . import views

urlpatterns = [
    path('request/', views.ChatRequestListCreateView.as_view(), name='chat-request-create'),
    path('requests/', views.ChatRequestListCreateView.as_view(), name='chat-requests-list'),
    path('request/<uuid:pk>/<str:action>/', views.ChatRequestActionView.as_view(), name='chat-request-action'),
    path('sessions/', views.ChatSessionListView.as_view(), name='chat-sessions-list'),
    path('sessions/<uuid:session_id>/messages/', views.MessageListCreateView.as_view(), name='chat-messages'),
]
