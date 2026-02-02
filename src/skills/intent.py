"""Intent detection skill using LLM."""

INTENTS = {
    "organize": "User wants to organize, consolidate, or structure their notes/wiki",
    "show_notes": "User wants to see, view, or read their notes or wiki",
    "show_reminders": "User wants to see their reminders or todos",
    "chat": "General conversation, questions, or anything else",
}

async def detect(llm_call, user_message: str) -> str:
    """Detect user intent from message. Returns one of: organize, show_notes, show_reminders, chat"""
    intent_list = "\n".join(f"- {k}: {v}" for k, v in INTENTS.items())

    prompt = f"""Classify this user message into ONE intent.

Intents:
{intent_list}

User message: {user_message}

Respond with ONLY the intent name (organize, show_notes, show_reminders, or chat). Nothing else."""

    result = await llm_call(prompt)
    intent = result.strip().lower()

    # Validate intent
    if intent in INTENTS:
        return intent
    return "chat"
