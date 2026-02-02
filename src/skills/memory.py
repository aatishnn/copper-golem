from datetime import datetime
from src.storage import get_user_dir
from src import llm

def get_memory_file(user_id: str):
    return get_user_dir(user_id) / "memory.md"

def read(user_id: str) -> str:
    f = get_memory_file(user_id)
    if not f.exists():
        f.write_text("# Memory\n\n")
    return f.read_text()

def append(user_id: str, content: str):
    f = get_memory_file(user_id)
    if not f.exists():
        f.write_text("# Memory\n\n")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(f, "a") as file:
        file.write(f"\n## {timestamp}\n{content}\n")

async def extract_and_store(user_id: str, user_message: str, assistant_response: str):
    """LLM-powered skill: Extract facts worth remembering from conversation."""
    prompt = f"""Extract any facts, preferences, or important details worth remembering from this conversation.
Be concise but preserve important details. If nothing worth remembering, respond with "NOTHING".

User: {user_message}
Assistant: {assistant_response}

Extracted facts (markdown bullet points, or NOTHING):"""

    result = await llm.call(prompt)
    if result.strip().upper() != "NOTHING":
        append(user_id, result)
