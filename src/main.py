"""Command line interface for Scribe."""

from datetime import datetime
from pathlib import Path
import sys

from config import OUTPUT_DIR
from summary import generate_summary
from transcription import transcribe


def _save_summary(markdown: str) -> Path:
    """Save the generated Markdown report in the output directory."""

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_path = OUTPUT_DIR / f"summary_{timestamp}.md"
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def main() -> int:
    """Run Scribe from the command line."""

    if len(sys.argv) != 2:
        print("Usage : python src/main.py examples/audio.wav")
        return 1

    audio_path = sys.argv[1]

    try:
        print("Transcription...")
        transcription = transcribe(audio_path)

        print("Résumé...")
        summary = generate_summary(transcription)
        output_path = _save_summary(summary)

        print()
        print(summary)
        print()
        print("Compte-rendu généré.")
        print(f"Fichier sauvegardé : {output_path}")
        return 0
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"Erreur : {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
