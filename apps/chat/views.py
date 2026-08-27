from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Q
from .models import ChatRequest, ChatSession, Message
from .serializers import ChatRequestSerializer, ChatSessionSerializer, MessageSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

class ChatRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatRequest.objects.filter(receiver=self.request.user, status='pending')

    def create(self, request, *args, **kwargs):
        receiver_username = request.data.get('receiver')
        if not receiver_username:
            return Response({'error': 'Receiver username is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        receiver = get_object_or_404(User, username=receiver_username)
        if receiver == request.user:
            return Response({'error': 'Cannot send a chat request to yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already a session
        session = ChatSession.objects.filter(
            Q(participant1=request.user, participant2=receiver) |
            Q(participant1=receiver, participant2=request.user)
        ).first()
        
        if session:
            return Response({'message': 'A chat session already exists', 'session_id': session.id}, status=status.HTTP_200_OK)

        # Check existing request
        req, created = ChatRequest.objects.get_or_create(
            sender=request.user, receiver=receiver,
            defaults={'status': 'pending'}
        )
        if not created and req.status == 'pending':
            return Response({'message': 'Request already sent', 'request_id': req.id}, status=status.HTTP_200_OK)
        
        # If it was rejected previously, reset to pending
        if req.status == 'rejected':
            req.status = 'pending'
            req.save()

        serializer = self.get_serializer(req)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ChatRequestActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, action):
        chat_request = get_object_or_404(ChatRequest, pk=pk, receiver=request.user)
        if chat_request.status != 'pending':
            return Response({'error': f'Request is already {chat_request.status}'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'accept':
            chat_request.status = 'accepted'
            chat_request.save()
            # Create session
            session = ChatSession.objects.create(
                participant1=chat_request.sender,
                participant2=chat_request.receiver
            )
            return Response({'message': 'Accepted', 'session_id': session.id})
        elif action == 'reject':
            chat_request.status = 'rejected'
            chat_request.save()
            return Response({'message': 'Rejected'})
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

class ChatSessionListView(generics.ListAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(
            Q(participant1=self.request.user) | Q(participant2=self.request.user)
        ).order_by('-updated_at')

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_session(self):
        session_id = self.kwargs['session_id']
        session = get_object_or_404(ChatSession, id=session_id)
        if self.request.user != session.participant1 and self.request.user != session.participant2:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You are not part of this chat.")
        return session

    def get_queryset(self):
        session = self.get_session()
        return session.messages.all().order_by('created_at')

    def create(self, request, *args, **kwargs):
        session = self.get_session()
        content = request.data.get('content')
        if not content:
            return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        msg = Message(session=session, sender=request.user)
        msg.set_content(content)
        msg.save()
        
        # update session updated_at
        session.updated_at = msg.created_at
        session.save()

        serializer = self.get_serializer(msg)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
