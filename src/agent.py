import os
from openai import AsyncOpenAI
from src.common import escape_markdown, config
from src.skills import memory, reminders, intent

client = AsyncOpenAI(
    #base_url="https://openrouter.ai/api/v1",
    base_url="http://192.168.1.142:4000",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

def get_model(usage: str) -> str:
    """Get model for a specific usage type from config."""
    return config.get("models", {}).get(usage, "google/gemini-2.0-flash-001")

async def llm_call(prompt: str, usage: str = "extraction") -> str:
    """Generic LLM call with configurable model based on usage."""
    model = get_model(usage)
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
    )
    return response.choices[0].message.content

async def handle_organize(user_id: str) -> str:
    """Handle organize intent."""
    from src.consolidate import consolidate_and_tree
    return await consolidate_and_tree(user_id)

async def handle_show_notes(user_id: str) -> str:
    """Handle show_notes intent."""
    from src.consolidate import get_wiki_tree
    wiki_content = memory.read(user_id)
    tree = get_wiki_tree(user_id)

    if not wiki_content.strip():
        return "You don't have any notes yet. Just chat with me and I'll remember important things!"

    return f"📝 Your Notes:\n\n{tree}"

async def handle_show_reminders(user_id: str) -> str:
    """Handle show_reminders intent."""
    reminder_content = reminders.read(user_id)

    if not reminder_content.strip():
        return "You don't have any reminders yet. Just say 'remind me to...' and I'll track it!"

    return f"⏰ Your Reminders:\n\n{reminder_content}"

async def chat(user_id: str, user_message: str) -> str:
    # Detect intent using LLM
    intent_call = lambda p: llm_call(p, "extraction")
    detected_intent = await intent.detect(intent_call, user_message)

    # Handle special intents
    if detected_intent == "organize":
        return await handle_organize(user_id)
    elif detected_intent == "show_notes":
        return await handle_show_notes(user_id)
    elif detected_intent == "show_reminders":
        return await handle_show_reminders(user_id)

    # Default: chat
    user_memory = escape_markdown(memory.read(user_id), version=2)
    user_reminders = escape_markdown(reminders.read(user_id), version=2)

    system = f"""You are a helpful personal assistant with memory. You remember details about the user and help them stay organized.

## Your Memory
{user_memory}

## Active Reminders
{user_reminders}

## Instructions
Be conversational and helpful. If the user mentions something worth remembering (facts, preferences, plans), acknowledge it naturally.

For reminders:
- If the user mentions a reminder WITHOUT a specific time, ask when they want to be reminded
- If the user mentions a reminder WITH a specific time, confirm you'll remind them at that time
- Do NOT confirm you'll track a reminder until you have a specific time"""

    model = get_model("chat")
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        max_tokens=1000,
    )
    assistant_response = response.choices[0].message.content

    # Use extraction model for these
    extraction_call = lambda p: llm_call(p, "extraction")
    await memory.extract_and_store(extraction_call, user_id, user_message, assistant_response)
    await reminders.extract_and_store(extraction_call, user_id, user_message)

    return assistant_response
