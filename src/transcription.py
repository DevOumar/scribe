"""Audio transcription service using Groq Speech-to-Text."""

from pathlib import Path

from groq import APIError, Groq

from config import load_settings


def transcribe(audio_path: str) -> str:
    """Transcribe an audio file with Groq Whisper.

    Args:
        audio_path: Path to the audio file to transcribe.

    Returns:
        The transcription text returned by Groq.

    Raises:
        FileNotFoundError: If the audio file does not exist.
        RuntimeError: If the Groq API request fails or returns no text.
    """

    path = Path(audio_path)
    if not path.is_file():
        raise FileNotFoundError(f"Fichier audio introuvable : {audio_path}")

    settings = load_settings()
    client = Groq(api_key=settings.groq_api_key)

    try:
        with path.open("rb") as audio_file:
            response = client.audio.transcriptions.create(
                file=(path.name, audio_file),
                model=settings.whisper_model,
                response_format="verbose_json",
            )
    except APIError as exc:
        raise RuntimeError(f"Erreur API Groq pendant la transcription : {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Erreur pendant la transcription : {exc}") from exc

    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("La transcription Groq ne contient aucun texte.")

    return text.strip()
