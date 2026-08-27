import os
from dotenv import find_dotenv, load_dotenv
from google import genai

# Load environment variables from .env file
load_dotenv(find_dotenv(usecwd=True))


def call_llm(prompt: str, model: str | None = None) -> str:
    """Send a prompt to Gemini LLM via google-genai client and return response text.

    Args:
        prompt: The input prompt string.
        model: Optional model identifier. Defaults to GEMINI_MODEL env var or 'gemini-2.5-flash'.

    Returns:
        str: Response text from the model.

    Raises:
        ValueError: If GEMINI_API_KEY is not set.
        RuntimeError: If the API call fails or returns empty content.
    """
    # Reload in case .env was modified at runtime
    load_dotenv(find_dotenv(usecwd=True))
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set in environment or .env file. "
            "Please configure your GEMINI_API_KEY."
        )

    selected_model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=selected_model,
            contents=prompt,
        )

        if response.text is not None:
            return response.text.strip()
        
        raise RuntimeError("Gemini returned an empty response.")
    except Exception as e:
        raise RuntimeError(f"Error calling LLM: {str(e)}") from e
