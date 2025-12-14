from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from typing import Optional

def get_mcq_prompt_template(persona_prompt: Optional[str] = None) -> PromptTemplate:
    """
    Get MCQ prompt template with optional persona.
    
    Args:
        persona_prompt: Optional system prompt for persona
    
    Returns:
        PromptTemplate instance
    """
    base_template = (
        "Generate a {difficulty} multiple-choice question about {topic}.\n\n"
        "IMPORTANT: Return ONLY a valid JSON object with these exact fields:\n"
        "- 'question': A clear, specific question (string)\n"
        "- 'options': An array of EXACTLY 4 possible answers (array of strings)\n"
        "- 'correct_answer': One of the options that is the correct answer (string)\n\n"
        "CRITICAL REQUIREMENTS:\n"
        "1. The 'options' array MUST contain exactly 4 strings\n"
        "2. The 'correct_answer' MUST be an exact match (including case and spacing) of one of the options\n"
        "3. Return ONLY the JSON object, no additional text or markdown formatting\n\n"
        "Example format:\n"
        '{{\n'
        '    "question": "What is the capital of France?",\n'
        '    "options": ["London", "Berlin", "Paris", "Madrid"],\n'
        '    "correct_answer": "Paris"\n'
        '}}\n\n'
        "Your response (JSON only):"
    )
    
    if persona_prompt:
        template = f"{persona_prompt}\n\n{base_template}"
    else:
        template = base_template
    
    return PromptTemplate(
        template=template,
        input_variables=["topic", "difficulty"]
    )


def get_fill_blank_prompt_template(persona_prompt: Optional[str] = None) -> PromptTemplate:
    """
    Get fill-in-the-blank prompt template with optional persona.
    
    Args:
        persona_prompt: Optional system prompt for persona
    
    Returns:
        PromptTemplate instance
    """
    base_template = (
        "Generate a {difficulty} fill-in-the-blank question about {topic}.\n\n"
        "Return ONLY a JSON object with these exact fields:\n"
        "- 'question': A sentence with '_____' marking where the blank should be\n"
        "- 'answer': The correct word or phrase that belongs in the blank\n\n"
        "Example format:\n"
        '{{\n'
        '    "question": "The capital of France is _____.",\n'
        '    "answer": "Paris"\n'
        '}}\n\n'
        "Your response:"
    )
    
    if persona_prompt:
        template = f"{persona_prompt}\n\n{base_template}"
    else:
        template = base_template
    
    return PromptTemplate(
        template=template,
        input_variables=["topic", "difficulty"]
    )


# Legacy templates for backward compatibility
mcq_prompt_template = get_mcq_prompt_template()
fill_blank_prompt_template = get_fill_blank_prompt_template()