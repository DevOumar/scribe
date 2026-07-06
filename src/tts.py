"""Text-to-Speech generation for Scribe summaries."""

from datetime import datetime
from pathlib import Path

from groq import APIError, Groq

from config import OUTPUT_DIR, load_settings


def _clean_markdown_for_speech(markdown: str) -> str:
    """Convert a short Markdown report into readable text for TTS."""

    replacements = {
        "#": "",
        "*": "",
        "- ": "",
        "`": "",
    }
    speech_text = markdown
    for old, new in replacements.items():
        speech_text = speech_text.replace(old, new)

    return speech_text.strip()[:3500]


def generate_speech(markdown: str) -> Path:
    """Generate an audio file from a Markdown summary using Groq TTS."""

    speech_text = _clean_markdown_for_speech(markdown)
    if not speech_text:
        raise ValueError("Le compte-rendu est vide, impossible de generer l'audio.")

    settings = load_settings()
    client = Groq(api_key=settings.groq_api_key)

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_path = OUTPUT_DIR / f"summary_audio_{timestamp}.wav"

    try:
        response = client.audio.speech.create(
            model=settings.tts_model,
            voice=settings.tts_voice,
            input=speech_text,
            response_format="wav",
        )
        response.write_to_file(output_path)
    except APIError as exc:
        error_text = str(exc)
        if "model_terms_required" in error_text:
            raise RuntimeError(
                "Le modele TTS Groq demande l'acceptation des conditions "
                "dans la console Groq avant la premiere utilisation."
            ) from exc
        raise RuntimeError(f"Erreur API Groq pendant la synthese vocale : {exc}") from exc

    return output_path
