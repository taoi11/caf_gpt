"""
PolicyFoo app models.
"""
from django.db import models
from core.models import TimeStampedModel


class PolicyDocument(TimeStampedModel):
    """
    Model to store policy documents.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    document_id = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.title


class PolicyQuery(TimeStampedModel):
    """
    Model to store policy queries.
    """
    query_text = models.TextField()
    user_identifier = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Query: {self.query_text[:50]}..."


class PolicyResponse(TimeStampedModel):
    """
    Model to store policy responses.
    """
    query = models.ForeignKey(PolicyQuery, on_delete=models.CASCADE, related_name='responses')
    response_text = models.TextField()
    documents_referenced = models.ManyToManyField(PolicyDocument, related_name='referenced_in')
    
    def __str__(self):
        return f"Response to {self.query}" 