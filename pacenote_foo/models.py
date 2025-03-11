"""
PaceNoteFoo app models.
"""
from django.db import models
from core.models import TimeStampedModel


class ChatSession(TimeStampedModel):
    """
    Model to store chat sessions.
    """
    session_id = models.UUIDField(unique=True)
    user_identifier = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Chat Session {self.session_id}"


class ChatMessage(TimeStampedModel):
    """
    Model to store chat messages.
    """
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    is_user = models.BooleanField(default=True)
    content = models.TextField()
    
    def __str__(self):
        return f"{'User' if self.is_user else 'System'} Message in {self.session}" 