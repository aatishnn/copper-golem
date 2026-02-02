import os
from openai import AsyncOpenAI
from src.common import escape_markdown, config
from src.skills import memory, reminders

ORGANIZE_TRIGGERS = ["organize my notes", "organize notes", "consolidate my notes", "consolidate notes"]

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

async def chat(user_id: str, user_message: str) -> str:
    # Check for organization intent
    if any(trigger in user_message.lower() for trigger in ORGANIZE_TRIGGERS):
        from src.consolidate import consolidate_and_tree
        return await consolidate_and_tree(user_id)

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
