import uuid
from django.db import models
from django.conf import settings
from .utils import encrypt_message, decrypt_message

User = settings.AUTH_USER_MODEL

class ChatRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, related_name='sent_chat_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_chat_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"Request from {self.sender} to {self.receiver} ({self.status})"


class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participant1 = models.ForeignKey(User, related_name='chat_sessions_as_p1', on_delete=models.CASCADE)
    participant2 = models.ForeignKey(User, related_name='chat_sessions_as_p2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('participant1', 'participant2')

    def __str__(self):
        return f"Chat between {self.participant1} and {self.participant2}"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    encrypted_content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_content(self, text):
        self.encrypted_content = encrypt_message(text)

    def get_content(self):
        return decrypt_message(self.encrypted_content)

    def __str__(self):
        return f"Message from {self.sender} in session {self.session.id}"
