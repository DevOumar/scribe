"""Application configuration for Scribe."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = ROOT_DIR / "prompts" / "system_prompt.txt"
OUTPUT_DIR = ROOT_DIR / "output"


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    groq_api_key: str
    whisper_model: str = "whisper-large-v3-turbo"
    llm_model: str = "llama-3.1-8b-instant"
    temperature: float = 0.2


def load_settings() -> Settings:
    """Load settings from a local .env file and environment variables."""

    load_dotenv(ROOT_DIR / ".env")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY est manquante. Créez un fichier .env à partir de "
            ".env.example et ajoutez votre clé Groq."
        )

    return Settings(groq_api_key=api_key)
