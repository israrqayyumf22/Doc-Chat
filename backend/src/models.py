from langchain_ollama import OllamaEmbeddings, ChatOllama
from .config import (
    MODEL_PROVIDER,
    OLLAMA_LLM_MODEL, 
    OLLAMA_EMBEDDING_MODEL,
    OPENAI_LLM_MODEL,
    OPENAI_EMBEDDING_MODEL,
    OPENAI_API_KEY
)

def get_embeddings_model(provider=None):
    """
    Returns the appropriate Embeddings model based on the provider.
    
    Args:
        provider (str): "ollama" or "openai". If None, uses MODEL_PROVIDER from config.
    
    Returns:
        Embeddings model instance (OllamaEmbeddings or OpenAIEmbeddings)
    """
    if provider is None:
        provider = MODEL_PROVIDER
    
    if provider.lower() == "openai":
        try:
            from langchain_openai import OpenAIEmbeddings
        except ImportError:
            raise ImportError(
                "OpenAI dependencies not installed. "
                "Run: pip install openai langchain-openai"
            )
        
        if not OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not set. Please set it as an environment variable."
            )
        
        return OpenAIEmbeddings(
            model=OPENAI_EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY
        )
    
    elif provider.lower() == "ollama":
        return OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
    
    else:
        raise ValueError(
            f"Unknown provider: {provider}. Use 'ollama' or 'openai'."
        )

def get_llm_model(provider=None):
    """
    Returns the appropriate LLM model based on the provider.
    
    Args:
        provider (str): "ollama" or "openai". If None, uses MODEL_PROVIDER from config.
    
    Returns:
        LLM model instance (ChatOllama or ChatOpenAI)
    """
    if provider is None:
        provider = MODEL_PROVIDER
    
    if provider.lower() == "openai":
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError(
                "OpenAI dependencies not installed. "
                "Run: pip install openai langchain-openai"
            )
        
        if not OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY not set. Please set it as an environment variable."
            )
        
        return ChatOpenAI(
            model=OPENAI_LLM_MODEL,
            openai_api_key=OPENAI_API_KEY,
            temperature=0.7
        )
    
    elif provider.lower() == "ollama":
        return ChatOllama(model=OLLAMA_LLM_MODEL)
    
    else:
        raise ValueError(
            f"Unknown provider: {provider}. Use 'ollama' or 'openai'."
        )
