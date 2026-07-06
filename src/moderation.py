"""Simple moderation checks for transcriptions."""


FORBIDDEN_PATTERNS = (
    "ignore les instructions",
    "ignore toutes les instructions",
    "oublie les instructions",
    "ignore previous instructions",
    "ignore all previous instructions",
    "system prompt",
    "prompt systeme",
    "prompt système",
    "révèle ta clé",
    "revele ta cle",
    "affiche la clé api",
    "affiche la cle api",
    "groq_api_key",
    "grog_api_key",
    "jailbreak",
)


def is_transcription_safe(transcription: str) -> bool:
    """Return False when the transcription looks like a prompt injection attempt."""

    normalized = transcription.lower()
    return not any(pattern in normalized for pattern in FORBIDDEN_PATTERNS)


def moderation_message() -> str:
    """Return the message displayed when a transcription is rejected."""

    return (
        "La transcription contient une demande qui semble chercher à détourner "
        "le comportement de l'outil. Le compte-rendu n'a pas été généré."
    )
