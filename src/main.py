"""Command line interface for Scribe."""

from datetime import datetime
from pathlib import Path
import sys

from config import OUTPUT_DIR
from moderation import is_transcription_safe, moderation_message
from summary import generate_summary
from transcription import transcribe


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


def main() -> int:
    """Run Scribe from the command line."""

    if len(sys.argv) not in (2, 3):
        print("Usage : python src/main.py examples/audio.wav [--save-transcription]")
        return 1

    audio_path = sys.argv[1]
    save_transcription = len(sys.argv) == 3 and sys.argv[2] == "--save-transcription"
    if len(sys.argv) == 3 and not save_transcription:
        print("Option inconnue. Utilisez : --save-transcription")
        return 1

    try:
        print("Transcription...")
        transcription = transcribe(audio_path)
        transcription_path = None
        if save_transcription:
            transcription_path = _save_transcription(transcription)

        if not is_transcription_safe(transcription):
            print(moderation_message())
            if transcription_path:
                print(f"Transcription sauvegardée : {transcription_path}")
            return 1

        print("Résumé...")
        summary = generate_summary(transcription)
        output_path = _save_summary(summary)

        print()
        print(summary)
        print()
        print("Compte-rendu généré.")
        print(f"Fichier sauvegardé : {output_path}")
        if transcription_path:
            print(f"Transcription sauvegardée : {transcription_path}")
        return 0
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
