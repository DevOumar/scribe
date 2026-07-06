"""Interactive questions about a generated Scribe summary."""

from groq import APIError, Groq

from config import load_settings


SYSTEM_PROMPT = (
    "Tu es l'assistant interactif de Scribe. "
    "Tu reponds uniquement a partir du compte-rendu fourni. "
    "Si l'information n'est pas presente dans le compte-rendu, "
    "dis clairement que le compte-rendu ne permet pas de repondre."
)


def answer_question(
    summary: str,
    question: str,
    history: list[tuple[str, str]] | None = None,
) -> str:
    """Answer one user question using only the generated summary."""

    if not summary.strip():
        raise ValueError("Le compte-rendu est vide.")
    if not question.strip():
        raise ValueError("La question est vide.")

    settings = load_settings()
    client = Groq(api_key=settings.groq_api_key)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Compte-rendu de reference :\n{summary}"},
    ]

    for previous_question, previous_answer in history or []:
        messages.append({"role": "user", "content": previous_question})
        messages.append({"role": "assistant", "content": previous_answer})

    messages.append({"role": "user", "content": question})

    try:
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            temperature=settings.temperature,
        )
    except APIError as exc:
        raise RuntimeError(f"Erreur API Groq pendant le mode historique : {exc}") from exc

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("La reponse du LLM est vide.")

    return content.strip()


def start_history(summary: str) -> None:
    """Start an interactive question-answer session about the summary."""

    conversation_history: list[tuple[str, str]] = []

    print()
    print("Mode historique. Posez une question sur le compte-rendu.")
    print("Appuyez sur Entree, ou tapez 'exit', pour quitter.")

    while True:
        question = input("Question : ").strip()
        if not question or question.lower() in {"exit", "quit"}:
            print("Fin du mode historique.")
            return

        answer = answer_question(summary, question, conversation_history)
        conversation_history.append((question, answer))

        print()
        print(answer)
        print()
