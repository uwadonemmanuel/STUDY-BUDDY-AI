from langchain_core.output_parsers import PydanticOutputParser
from src.models.question_schemas import MCQQuestion,FillBlankQuestion
from src.prompts.templates import get_mcq_prompt_template, get_fill_blank_prompt_template
from src.llm.groq_client import get_llm
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException
from typing import Optional


class QuestionGenerator:
    def __init__(self, provider: str = None, model_name: str = None, temperature: float = None, persona: str = None):
        """
        Initialize QuestionGenerator with optional model and persona settings.
        
        Args:
            provider: LLM provider ('groq' or 'openai')
            model_name: Specific model name
            temperature: Temperature setting
            persona: Chatbot persona key
        """
        self.provider = provider or settings.DEFAULT_PROVIDER
        self.model_name = model_name or settings.DEFAULT_MODEL
        self.temperature = temperature if temperature is not None else settings.TEMPERATURE
        self.persona = persona or settings.DEFAULT_PERSONA
        
        # Get persona system prompt
        self.persona_prompt = None
        if self.persona and self.persona in settings.CHATBOT_PERSONAS:
            self.persona_prompt = settings.CHATBOT_PERSONAS[self.persona]["system_prompt"]
        
        # Initialize LLM
        self.llm = get_llm(
            provider=self.provider,
            model_name=self.model_name,
            temperature=self.temperature,
            persona=self.persona
        )
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info(f"Initialized QuestionGenerator with provider={self.provider}, model={self.model_name}, persona={self.persona}")
        
        # Store fallback model mapping for GPT-5
        self.gpt5_fallbacks = {
            "gpt-5": "gpt-4o",
            "gpt-5-mini": "gpt-4o-mini",
            "gpt-5-nano": "gpt-4o-mini",
        }

    def _retry_and_parse(self, prompt, parser, topic, difficulty):
        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(f"Generating question for topic {topic} with difficulty {difficulty} using {self.provider}/{self.model_name}")

                formatted_prompt = prompt.format(topic=topic, difficulty=difficulty)
                response = self.llm.invoke(formatted_prompt)

                # Log raw response for debugging (first 500 chars)
                self.logger.debug(f"Raw LLM response (first 500 chars): {response.content[:500]}")

                parsed = parser.parse(response.content)

                self.logger.info("Successfully parsed the question")
                return parsed
            
            except Exception as e:
                error_str = str(e)
                self.logger.error(f"Error on attempt {attempt + 1}: {error_str}")
                
                # Check for GPT-5 model not found errors and try fallback
                if ("model_not_found" in error_str.lower() or "does not exist" in error_str.lower()) and \
                   self.provider.lower() == "openai" and \
                   self.model_name.lower().startswith("gpt-5"):
                    fallback_model = self.gpt5_fallbacks.get(self.model_name.lower())
                    if fallback_model and attempt < settings.MAX_RETRIES - 1:
                        self.logger.warning(f"GPT-5 model {self.model_name} not available. Trying fallback: {fallback_model}")
                        # Reinitialize LLM with fallback model
                        self.llm = get_llm(
                            provider=self.provider,
                            model_name=fallback_model,
                            temperature=self.temperature,
                            persona=self.persona
                        )
                        self.model_name = fallback_model
                        continue  # Retry with fallback model
                
                # Check for decommissioned model errors
                if "decommissioned" in error_str.lower() or "model_decommissioned" in error_str.lower():
                    self.logger.error(f"Model {self.model_name} has been decommissioned. Please update to a supported model.")
                    raise CustomException(
                        f"Model {self.model_name} has been decommissioned. Please select a different model from the dropdown.",
                        e
                    )
                
                # Log the raw response if available for debugging
                if hasattr(e, 'response') and hasattr(e.response, 'content'):
                    self.logger.error(f"Failed response content: {e.response.content[:500]}")
                
                if attempt == settings.MAX_RETRIES - 1:
                    raise CustomException(f"Generation failed after {settings.MAX_RETRIES} attempts", e)
    
    def generate_mcq(self, topic: str, difficulty: str = 'medium') -> MCQQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=MCQQuestion)
            prompt_template = get_mcq_prompt_template(self.persona_prompt)

            question = self._retry_and_parse(prompt_template, parser, topic, difficulty)

            # Validate MCQ structure with better error handling
            if len(question.options) != 4:
                self.logger.error(f"Invalid number of options: {len(question.options)}. Expected 4. Options: {question.options}")
                raise ValueError(f"Invalid MCQ Structure: Expected 4 options, got {len(question.options)}")
            
            # Normalize options and correct answer for comparison (strip whitespace, case-insensitive)
            normalized_options = [opt.strip().lower() for opt in question.options]
            normalized_correct = question.correct_answer.strip().lower()
            
            # Check if correct answer matches any option (case-insensitive, whitespace-insensitive)
            if normalized_correct not in normalized_options:
                # Try to find a partial match
                matches = [opt for opt in normalized_options if normalized_correct in opt or opt in normalized_correct]
                if matches:
                    # Use the first match
                    matched_index = normalized_options.index(matches[0])
                    question.correct_answer = question.options[matched_index]  # Use original case
                    self.logger.warning(f"Correct answer '{question.correct_answer}' didn't match exactly, but found match: '{question.options[matched_index]}'")
                else:
                    self.logger.error(f"Correct answer '{question.correct_answer}' not found in options: {question.options}")
                    raise ValueError(f"Invalid MCQ Structure: Correct answer '{question.correct_answer}' not found in options: {question.options}")
            
            # Ensure correct_answer uses the exact option text (preserve original formatting)
            if question.correct_answer not in question.options:
                # Find the matching option with original case
                for opt in question.options:
                    if opt.strip().lower() == normalized_correct:
                        question.correct_answer = opt
                        break
            
            self.logger.info(f"Generated a valid MCQ Question: {question.question[:50]}...")
            return question
        
        except ValueError as e:
            self.logger.error(f"MCQ validation failed: {str(e)}")
            raise CustomException(f"MCQ generation failed: {str(e)}", e)
        except Exception as e:
            self.logger.error(f"Failed to generate MCQ : {str(e)}")
            raise CustomException("MCQ generation failed", e)
    
    def generate_fill_blank(self, topic: str, difficulty: str = 'medium') -> FillBlankQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)
            prompt_template = get_fill_blank_prompt_template(self.persona_prompt)

            question = self._retry_and_parse(prompt_template, parser, topic, difficulty)

            if "___" not in question.question:
                raise ValueError("Fill in blanks should contain '___'")
            
            self.logger.info("Generated a valid Fill in Blanks Question")
            return question
        
        except Exception as e:
            self.logger.error(f"Failed to generate fillups : {str(e)}")
            raise CustomException("Fill in blanks generation failed", e)

