from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def get_user_dir(user_id: str) -> Path:
    user_dir = DATA_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir

def get_memory_file(user_id: str) -> Path:
    return get_user_dir(user_id) / "memory.md"

def read_memory(user_id: str) -> str:
    f = get_memory_file(user_id)
    if not f.exists():
        f.write_text("# Memory\n\n")
    return f.read_text()

def append_memory(user_id: str, content: str):
    f = get_memory_file(user_id)
    if not f.exists():
        f.write_text("# Memory\n\n")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(f, "a") as file:
        file.write(f"\n## {timestamp}\n{content}\n")

async def extract_and_store_memory(llm_call, user_id: str, user_message: str, assistant_response: str):
    prompt = f"""Extract any facts, preferences, or important details worth remembering from this conversation.
Be concise but preserve important details. If nothing worth remembering, respond with "NOTHING".

User: {user_message}
Assistant: {assistant_response}

Extracted facts (markdown bullet points, or NOTHING):"""

    result = await llm_call(prompt)
    if result.strip().upper() != "NOTHING":
        append_memory(user_id, result)
