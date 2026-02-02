import os
from openai import AsyncOpenAI

from memory import read_memory, extract_and_store_memory
from reminders import read_reminders, extract_and_store_reminder

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

MODEL = "google/gemini-2.0-flash-001"

async def llm_call(prompt: str) -> str:
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
    )
    return response.choices[0].message.content

async def chat(user_id: str, user_message: str) -> str:
    memory = read_memory(user_id)
    reminders = read_reminders(user_id)

    system = f"""You are a helpful personal assistant with memory. You remember details about the user and help them stay organized.

## Your Memory
{memory}

## Active Reminders
{reminders}

Be conversational and helpful. If the user mentions something worth remembering (facts, preferences, plans), acknowledge it naturally. If they mention a task or reminder, confirm you'll track it."""

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
        max_tokens=1000,
    )
    assistant_response = response.choices[0].message.content

    await extract_and_store_memory(llm_call, user_id, user_message, assistant_response)
    await extract_and_store_reminder(llm_call, user_id, user_message)

    return assistant_response
