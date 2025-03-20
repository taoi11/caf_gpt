"""
Service for policy document retrieval and processing.
"""
import logging

from core.services import OpenRouterService
from ..models import PolicyDocument, PolicyQuery, PolicyResponse

logger = logging.getLogger(__name__)


class PolicyService:
    """
    Service for retrieving and processing policy documents.
    """

    def __init__(self):
        """
        Initialize the policy service.
        """
        self.openrouter_service = OpenRouterService()

    def search_documents(self, query_text):
        """
        Search documents based on query text.
        
        Args:
            query_text: The text to search for.
            
        Returns:
            List of matching documents.
        """
        # In a real implementation, this would use a more sophisticated search
        # like vector similarity search or keyword extraction
        documents = PolicyDocument.objects.filter(
            content__icontains=query_text
        ).order_by('-updated_at')[:5]
        
        return documents

    def generate_response(self, query_text, documents=None):
        """
        Generate a response based on query and available documents.
        
        Args:
            query_text: The query text.
            documents: Optional list of documents to use for generation.
            
        Returns:
            Generated response and citations.
        """
        # If documents not provided, search for them
        if documents is None:
            documents = self.search_documents(query_text)
            
        # Format documents for prompt
        document_content = ""
        for i, doc in enumerate(documents):
            document_content += f"Document {i+1}: {doc.title}\n"
            document_content += f"{doc.content}\n\n"
            
        # Construct prompt
        prompt = f"""
        User Query: {query_text}
        
        Available Documents:
        {document_content}
        
        Please provide a concise answer to the user query based only on the information in the available documents.
        If the documents don't contain the answer, just say that you don't have enough information.
        Make sure to cite the documents you used in your answer.
        """
        
        # Generate response using LLM
        try:
            llm_response = self.openrouter_service.generate_completion(prompt)
            
            # Save the query and response to database
            query = PolicyQuery.objects.create(
                query_text=query_text,
            )
            
            response = PolicyResponse.objects.create(
                query=query,
                response_text=llm_response
            )
            
            # Add references to the documents
            response.documents_referenced.add(*documents)
            
            # Format citations for API response
            citations = []
            for doc in documents:
                citations.append({
                    'document_id': doc.document_id,
                    'title': doc.title,
                    'excerpt': doc.content[:200] + '...' if len(doc.content) > 200 else doc.content
                })
                
            return {
                'response': llm_response,
                'citations': citations
            }
            
        except Exception as e:
            logger.error(f"Error generating policy response: {e}")
            return {
                'response': "Sorry, I encountered an error while generating a response.",
                'citations': []
            }
