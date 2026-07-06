"""Command line interface for Scribe."""

from datetime import datetime
from pathlib import Path
import sys

from config import OUTPUT_DIR
from history import start_history
from moderation import is_transcription_safe, moderation_message
from summary import generate_summary
from transcription import transcribe
from tts import generate_speech


ALLOWED_OPTIONS = {"--save-transcription", "--tts", "--history"}


def _save_summary(markdown: str) -> Path:
    """Save the generated Markdown report in the output directory."""

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_path = OUTPUT_DIR / f"summary_{timestamp}.md"
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def _save_transcription(transcription: str) -> Path:
    """Save the raw transcription in the output directory."""

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_path = OUTPUT_DIR / f"transcription_{timestamp}.txt"
    output_path.write_text(transcription, encoding="utf-8")
    return output_path


def _parse_options(arguments: list[str]) -> tuple[str, bool, bool, bool]:
    """Parse the audio path and optional CLI flags."""

    if not arguments:
        raise ValueError(
            "Usage : python src/main.py examples/audio.wav "
            "[--save-transcription] [--tts] [--history]"
        )

    audio_path = arguments[0]
    options = set(arguments[1:])
    unknown_options = options - ALLOWED_OPTIONS
    if unknown_options:
        raise ValueError(
            "Option inconnue. Utilisez : --save-transcription, --tts ou --history"
        )

    save_transcription = "--save-transcription" in options
    generate_audio = "--tts" in options
    interactive_history = "--history" in options
    return audio_path, save_transcription, generate_audio, interactive_history


def main() -> int:
    """Run Scribe from the command line."""

    try:
        audio_path, save_transcription, generate_audio, interactive_history = (
            _parse_options(sys.argv[1:])
        )

        print("Transcription...")
        transcription = transcribe(audio_path)
        transcription_path = None
        if save_transcription:
            transcription_path = _save_transcription(transcription)

        if not is_transcription_safe(transcription):
            print(moderation_message())
            if transcription_path:
                print(f"Transcription sauvegardee : {transcription_path}")
            return 1

        print("Resume...")
        summary = generate_summary(transcription)
        output_path = _save_summary(summary)

        print()
        print(summary)
        print()
        print("Compte-rendu genere.")
        print(f"Fichier sauvegarde : {output_path}")
        if transcription_path:
            print(f"Transcription sauvegardee : {transcription_path}")

        if generate_audio:
            print("Synthese vocale...")
            speech_path = generate_speech(summary)
            print(f"Audio sauvegarde : {speech_path}")

        if interactive_history:
            start_history(summary)

        return 0
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
