"""Meeting summary generation using Groq Chat Completions."""

from groq import APIError, Groq

from config import PROMPT_PATH, load_settings


def _load_system_prompt() -> str:
    """Read the system prompt used to guide the LLM."""

    if not PROMPT_PATH.is_file():
        raise FileNotFoundError(f"Prompt système introuvable : {PROMPT_PATH}")

    return PROMPT_PATH.read_text(encoding="utf-8")


def generate_summary(transcription: str) -> str:
    """Generate a Markdown report from an audio transcription.

    Args:
        transcription: Raw transcription text.

    Returns:
        A Markdown meeting report.

    Raises:
        ValueError: If the transcription is empty.
        RuntimeError: If the Groq API request fails or returns no content.
    """

    if not transcription.strip():
        raise ValueError("La transcription est vide.")

    settings = load_settings()
    client = Groq(api_key=settings.groq_api_key)
    system_prompt = _load_system_prompt()

    try:
        response = client.chat.completions.create(
            model=settings.llm_model,
            temperature=settings.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcription},
            ],
        )
    except APIError as exc:
        raise RuntimeError(f"Erreur API Groq pendant le résumé : {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Erreur pendant le résumé : {exc}") from exc

    if not response.choices:
        raise RuntimeError("Le modèle Groq n'a retourné aucun choix.")

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Le modèle Groq n'a retourné aucun compte-rendu.")

    return content.strip()
