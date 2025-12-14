import os
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

class Settings():
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Default model settings
    DEFAULT_MODEL = "llama-3.1-8b-instant"
    DEFAULT_PROVIDER = "groq"
    TEMPERATURE = 0.9
    MAX_RETRIES = 3
    
    # Available models by provider
    # Note: Models are verified as of January 2025
    # Deprecated/decommissioned models have been removed:
    # - o1-preview (deprecated July 28, 2025) -> replaced with o3
    # - o1-mini (deprecated October 27, 2025) -> replaced with o4-mini
    # - llama-3.1-70b-versatile (decommissioned) -> replaced with llama-3.3-70b-versatile
    # - llama-3.1-405b-reasoning (not available/not accessible) -> removed
    # - mixtral-8x7b-32768 (decommissioned) -> removed
    # - gemma-7b-it (decommissioned) -> removed
    # - gemma2-9b-it (decommissioned) -> removed
    # 
    # IMPORTANT: Check https://console.groq.com/docs/models for the latest available models
    AVAILABLE_MODELS: Dict[str, List[str]] = {
        "groq": [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile"  # Currently available model
        ],
        "openai": [
            # GPT-5 Series (May require API access or future availability)
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-nano",
            # GPT-4 Series (Verified Available)
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            # Reasoning Models (o-series) - Verified Available
            "o3",
            "o4-mini"
        ]
    }
    
    # Chatbot personas
    CHATBOT_PERSONAS: Dict[str, Dict[str, str]] = {
        "friendly_tutor": {
            "name": "Friendly Tutor",
            "description": "Encouraging and supportive, explains concepts clearly",
            "system_prompt": "You are a friendly and encouraging tutor. You help students learn by explaining concepts clearly and providing positive reinforcement. Always be patient and supportive."
        },
        "strict_professor": {
            "name": "Strict Professor",
            "description": "Academic and precise, expects high standards",
            "system_prompt": "You are a strict but fair professor. You maintain high academic standards and provide detailed, precise explanations. Challenge students to think critically."
        },
        "casual_buddy": {
            "name": "Casual Study Buddy",
            "description": "Relaxed and conversational, makes learning fun",
            "system_prompt": "You are a casual study buddy. You make learning fun and engaging with a relaxed, conversational style. Use examples and analogies to make concepts relatable."
        },
        "socratic_teacher": {
            "name": "Socratic Teacher",
            "description": "Asks questions to guide learning, promotes critical thinking",
            "system_prompt": "You are a Socratic teacher. Instead of giving direct answers, you ask thoughtful questions to guide students to discover answers themselves. Encourage critical thinking."
        },
        "technical_expert": {
            "name": "Technical Expert",
            "description": "Deep technical knowledge, detailed explanations",
            "system_prompt": "You are a technical expert with deep knowledge. Provide detailed, accurate technical explanations. Use proper terminology and explain complex concepts thoroughly."
        },
        "creative_mentor": {
            "name": "Creative Mentor",
            "description": "Uses creative approaches and real-world examples",
            "system_prompt": "You are a creative mentor. Use creative approaches, real-world examples, and engaging methods to help students understand concepts. Make learning memorable and fun."
        }
    }
    
    DEFAULT_PERSONA = "friendly_tutor"


settings = Settings()  