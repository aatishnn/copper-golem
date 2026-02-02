from src import llm
from src.skills import memory, reminders

async def chat(user_id: str, user_message: str) -> str:
    """Main agent: orchestrates skills and generates response."""
    # Load context
    user_memory = memory.read(user_id)
    user_reminders = reminders.read(user_id)

    system = f"""You are a helpful personal assistant with memory. You remember details about the user and help them stay organized.

## Your Memory
{user_memory}

## Active Reminders
{user_reminders}

Be conversational and helpful. If the user mentions something worth remembering (facts, preferences, plans), acknowledge it naturally. If they mention a task or reminder, confirm you'll track it."""

    # Generate response
    response = await llm.chat(system, user_message)

    # Run skills to extract and store information
    await memory.extract_and_store(user_id, user_message, response)
    await reminders.extract_and_store(user_id, user_message)

    return response
