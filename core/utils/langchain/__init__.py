"""
LangChain utilities module.
"""

from core.utils.langchain.base import (
    LangChainWrapper,
    OpenRouterChatModel,
    OpenRouterError,
)

from core.utils.langchain.document_loaders import (
    TextLoader,
    MarkdownLoader,
    S3DocumentLoader,
    DocumentLoaderError,
)

__all__ = [
    # Base
    'LangChainWrapper',
    'OpenRouterChatModel',
    'OpenRouterError',

    # Document Loaders
    'TextLoader',
    'MarkdownLoader',
    'S3DocumentLoader',
    'DocumentLoaderError',
]
