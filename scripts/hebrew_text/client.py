"""Gemini API client with retry logic and error handling."""

import os
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Lazy imports - only import when needed
# Try new google.genai first, fallback to deprecated google.generativeai
try:
    from google import genai
    USE_NEW_API = True
    from PIL import Image
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        import google.generativeai as genai_old
        USE_NEW_API = False
        from PIL import Image
        GEMINI_AVAILABLE = True
    except ImportError:
        GEMINI_AVAILABLE = False
        genai = None
        genai_old = None
        Image = None
        USE_NEW_API = False


class GeminiClient:
    """Gemini API client with retry logic and error handling."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize Gemini client with API key validation.

        Args:
            api_key: Google Gemini API key. If None, reads from GEMINI_API_KEY env var.
            model_name: Specific model to use.

        Raises:
            ValueError: If API key is not provided or invalid
            ImportError: If google-generativeai is not installed
        """
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-genai or google-generativeai is not installed. "
                "Install it with: pip install google-genai"
            )

        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Set it as environment variable or pass as argument.\n"
                "Get your API key from: https://aistudio.google.com/app/apikey"
            )

        self.api_key = api_key
        self.use_new_api = USE_NEW_API
        self.client = None
        self.model_name = None

        # Try different model names
        if model_name:
            model_names = [model_name]
        else:
            model_names = [
                'gemini-2.0-flash-exp',
                'gemini-1.5-pro-latest',
                'gemini-1.5-pro',
                'gemini-1.5-flash',
            ]

        if self.use_new_api:
            # Initialize new SDK client
            self.client = genai.Client(api_key=api_key)
            for name in model_names:
                try:
                    # Test if model exists/accessible
                    self.client.models.get(model=name)
                    self.model_name = name
                    logger.info(f"Using model (new SDK): {name}")
                    break
                except Exception:
                    continue
        else:
            # Initialize old SDK
            genai_old.configure(api_key=api_key)
            for name in model_names:
                try:
                    self.model = genai_old.GenerativeModel(name)
                    self.model_name = name
                    logger.info(f"Using model (old SDK): {name}")
                    break
                except Exception:
                    continue

        if self.model_name is None and not self.use_new_api:
            # Fallback for old SDK if loop failed
            try:
                self.model = genai_old.GenerativeModel('gemini-1.5-pro')
                self.model_name = 'gemini-1.5-pro'
            except Exception:
                pass

        if self.model_name is None:
            raise ValueError(
                f"None of the models {model_names} are available or accessible. "
                "Please check your API key and available models."
            )

    def transcribe_image(self, image_path: Path, prompt: str) -> Dict[str, Any]:
        """
        Send image to Gemini API and return response.

        Args:
            image_path: Path to image file
            prompt: Prompt text for transcription

        Returns:
            Dictionary with 'text' (response text) and 'usage' (token usage info)
        """
        def _call_api():
            # Load image
            image = Image.open(image_path)

            if self.use_new_api:
                # New SDK call with temperature=0 for deterministic output
                from google.genai import types
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt, image],
                    config=types.GenerateContentConfig(
                        temperature=0.0,  # Deterministic for OCR transcription
                    )
                )
                text = response.text if response.text else ""
                usage = {
                    'prompt_tokens': response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
                    'completion_tokens': response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
                    'total_tokens': response.usage_metadata.total_token_count if response.usage_metadata else 0
                }
            else:
                # Old SDK call with temperature=0 for deterministic output
                generation_config = {
                    "temperature": 0.0,  # Deterministic for OCR transcription
                }
                response = self.model.generate_content(
                    [prompt, image],
                    generation_config=generation_config
                )
                text = response.text if response.text else ""
                usage = {
                    'prompt_tokens': getattr(response.usage_metadata, 'prompt_token_count', 0),
                    'completion_tokens': getattr(response.usage_metadata, 'completion_token_count', 0),
                    'total_tokens': getattr(response.usage_metadata, 'total_token_count', 0)
                }

            return {
                'text': text,
                'usage': usage
            }

        return self._retry_with_backoff(_call_api, max_retries=5)

    def _retry_with_backoff(self, func, max_retries: int = 5) -> Any:
        """
        Exponential backoff retry logic.

        Args:
            func: Function to retry
            max_retries: Maximum number of retries

        Returns:
            Result from function

        Raises:
            Exception: If all retries fail
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                last_exception = e
                error_code = self._get_error_code(e)

                # Don't retry on 400 (bad request) or 401 (unauthorized)
                if error_code in [400, 401]:
                    logger.error(f"Non-retryable error ({error_code}): {e}")
                    raise

                # Handle rate limiting (429)
                if error_code == 429:
                    retry_after = self._get_retry_after(e)
                    wait_time = retry_after if retry_after else min(2 ** attempt, 60)
                    logger.warning(
                        f"Rate limit hit (attempt {attempt + 1}/{max_retries}). "
                        f"Waiting {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue

                # Handle server errors (500, 502, 503)
                if error_code in [500, 502, 503]:
                    wait_time = min(2 ** attempt, 60)
                    logger.warning(
                        f"Server error {error_code} (attempt {attempt + 1}/{max_retries}). "
                        f"Waiting {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue

                # Handle 404 errors (model not found)
                if error_code == 404 or '404' in str(e) or 'not found' in str(e).lower():
                    # Don't retry 404 errors - they won't resolve
                    logger.error(f"Model not found (404): {e}")
                    logger.error("Try using a different model name or check API documentation")
                    raise

                # Unknown error - retry with backoff
                wait_time = min(2 ** attempt, 60)
                logger.warning(
                    f"Error (attempt {attempt + 1}/{max_retries}): {e}. "
                    f"Waiting {wait_time}s..."
                )
                time.sleep(wait_time)

        # All retries exhausted
        logger.error(f"Failed after {max_retries} attempts: {last_exception}")
        raise last_exception

    def _get_error_code(self, error: Exception) -> Optional[int]:
        """
        Extract HTTP error code from exception.

        Args:
            error: Exception object

        Returns:
            HTTP status code or None
        """
        # Check for HTTP error codes in exception attributes
        if hasattr(error, 'status_code'):
            return error.status_code

        if hasattr(error, 'code'):
            return error.code

        # Check error message for common patterns
        error_str = str(error).lower()
        if '404' in error_str or 'not found' in error_str:
            return 404
        if '429' in error_str or 'rate limit' in error_str:
            return 429
        if '401' in error_str or 'unauthorized' in error_str or 'invalid api key' in error_str:
            return 401
        if '400' in error_str or 'bad request' in error_str:
            return 400
        if '500' in error_str or 'internal server error' in error_str:
            return 500
        if '502' in error_str or 'bad gateway' in error_str:
            return 502
        if '503' in error_str or 'service unavailable' in error_str:
            return 503

        return None

    def _get_retry_after(self, error: Exception) -> Optional[int]:
        """
        Extract Retry-After header value from exception.

        Args:
            error: Exception object

        Returns:
            Retry-After value in seconds or None
        """
        if hasattr(error, 'response') and hasattr(error.response, 'headers'):
            retry_after = error.response.headers.get('Retry-After')
            if retry_after:
                try:
                    return int(retry_after)
                except ValueError:
                    pass

        return None

    def _handle_error(self, error: Exception) -> None:
        """
        Handle different error types.

        Args:
            error: Exception to handle
        """
        error_code = self._get_error_code(error)

        if error_code == 401:
            logger.error(
                "API key is invalid or expired. "
                "Get a new key from: https://makersuite.google.com/app/apikey"
            )
        elif error_code == 429:
            logger.error("Rate limit exceeded. Please wait before retrying.")
        elif error_code in [500, 502, 503]:
            logger.error(f"Server error ({error_code}). Please try again later.")
        else:
            logger.error(f"Unexpected error: {error}")

    @staticmethod
    def estimate_cost() -> float:
        """
        Calculate estimated cost per image.

        Returns:
            Estimated cost in USD per image (~$0.00125)
        """
        # Gemini 1.5 Pro pricing (as of 2024):
        # Input: $1.25 per 1M tokens
        # Output: $5.00 per 1M tokens
        # Average image: ~1000 input tokens, ~500 output tokens
        # Cost: (1000/1M * $1.25) + (500/1M * $5.00) = $0.00125 + $0.0025 ≈ $0.00375
        # Using conservative estimate of $0.00125 per image
        return 0.00125


