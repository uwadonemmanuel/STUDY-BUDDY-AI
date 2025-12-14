from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from src.config.settings import settings
from src.common.logger import get_logger
from typing import Optional

logger = get_logger(__name__)

def get_llm(provider: str = None, model_name: str = None, temperature: float = None, persona: str = None) -> BaseChatModel:
    """
    Get LLM instance based on provider and model.
    
    Args:
        provider: LLM provider ('groq' or 'openai')
        model_name: Specific model name
        temperature: Temperature setting
        persona: Chatbot persona to use
    
    Returns:
        BaseChatModel instance
    """
    provider = provider or settings.DEFAULT_PROVIDER
    model_name = model_name or settings.DEFAULT_MODEL
    persona = persona or settings.DEFAULT_PERSONA
    
    # Check if model supports temperature
    # Reasoning models don't support temperature parameter
    reasoning_models = [
        "o3", "o4-mini"
    ]
    supports_temperature = model_name.lower() not in [m.lower() for m in reasoning_models]
    
    # Set temperature only if model supports it
    if supports_temperature:
        temperature = temperature if temperature is not None else settings.TEMPERATURE
    else:
        temperature = None  # Reasoning models don't use temperature
        logger.info(f"Model {model_name} is a reasoning model - temperature will not be applied")
    
    # Get persona system prompt if persona is specified
    system_prompt = None
    if persona and persona in settings.CHATBOT_PERSONAS:
        system_prompt = settings.CHATBOT_PERSONAS[persona]["system_prompt"]
        logger.info(f"Using persona: {settings.CHATBOT_PERSONAS[persona]['name']}")
    
    try:
        if provider.lower() == "groq":
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            # Map decommissioned/unavailable Groq models to their replacements
            groq_model_mapping = {
                "llama-3.1-70b-versatile": "llama-3.3-70b-versatile",  # Decommissioned, use 3.3
                "llama-3.1-405b-reasoning": "llama-3.3-70b-versatile",  # Not available, use 3.3 as fallback
                "mixtral-8x7b-32768": "llama-3.3-70b-versatile",  # Decommissioned, use 3.3 as fallback
                "gemma-7b-it": "llama-3.3-70b-versatile",  # Decommissioned, use 3.3 as fallback
                "gemma2-9b-it": "llama-3.3-70b-versatile",  # Decommissioned, use 3.3 as fallback
            }
            actual_model = groq_model_mapping.get(model_name.lower(), model_name)
            
            if actual_model != model_name:
                logger.warning(f"Model {model_name} has been decommissioned. Using replacement: {actual_model}")
            
            # Groq models support temperature
            llm = ChatGroq(
                api_key=settings.GROQ_API_KEY,
                model=actual_model,
                temperature=temperature if temperature is not None else settings.TEMPERATURE
            )
            logger.info(f"Initialized Groq LLM with model: {actual_model}, temperature: {temperature}")
            
        elif provider.lower() == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            # Map model names (handle legacy names and deprecated replacements)
            # Note: GPT-5 models will be tried first, fallback happens in error handling
            model_mapping = {
                # Legacy GPT-5 references
                "gpt-5-turbo": "gpt-5",  # Map to gpt-5
                # Deprecated models mapped to replacements
                "o1-preview": "o3",  # o1-preview deprecated, use o3
                "o1-mini": "o4-mini",  # o1-mini deprecated, use o4-mini
            }
            actual_model = model_mapping.get(model_name.lower(), model_name)
            
            # Determine fallback model for GPT-5 if not available
            gpt5_fallbacks = {
                "gpt-5": "gpt-4o",
                "gpt-5-mini": "gpt-4o-mini",
                "gpt-5-nano": "gpt-4o-mini",
            }
            fallback_model = gpt5_fallbacks.get(actual_model.lower())
            
            # Build ChatOpenAI kwargs - only include temperature if model supports it
            openai_kwargs = {
                "api_key": settings.OPENAI_API_KEY,
                "model": actual_model
            }
            
            # Only add temperature if the model supports it
            if supports_temperature and temperature is not None:
                openai_kwargs["temperature"] = temperature
            
            llm = ChatOpenAI(**openai_kwargs)
            logger.info(f"Initialized OpenAI LLM with model: {actual_model}, temperature: {temperature if supports_temperature else 'N/A (reasoning model)'}")
            
        else:
            raise ValueError(f"Unsupported provider: {provider}. Supported providers: groq, openai")
        
        # If persona system prompt is provided, we'll need to use it in prompts
        # This will be handled in the question generator
        if system_prompt:
            logger.info(f"Persona system prompt will be applied: {persona}")
        
        return llm
        
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {str(e)}")
        raise


def get_groq_llm():
    """Legacy function for backward compatibility"""
    return get_llm(provider="groq", model_name=settings.DEFAULT_MODEL)