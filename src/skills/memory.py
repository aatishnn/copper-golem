from datetime import datetime
from src.common import Storage, storage as default_storage

def get_memory_file(user_id: str, storage: Storage = None):
    s = storage or default_storage
    return s.get_user_dir(user_id) / "memory.md"

def get_log_file(user_id: str, storage: Storage = None):
    s = storage or default_storage
    return s.get_user_dir(user_id) / "log.md"

def read(user_id: str, storage: Storage = None) -> str:
    f = get_memory_file(user_id, storage)
    return f.read_text() if f.exists() else ""

def read_log(user_id: str, storage: Storage = None) -> str:
    f = get_log_file(user_id, storage)
    return f.read_text() if f.exists() else ""

def append(user_id: str, content: str, storage: Storage = None):
    f = get_memory_file(user_id, storage)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(f, "a") as file:
        file.write(f"\n## {timestamp}\n{content}\n")

def append_log(user_id: str, user_message: str, assistant_response: str, storage: Storage = None):
    """Append raw conversation to log file."""
    f = get_log_file(user_id, storage)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(f, "a") as file:
        file.write(f"\n## {timestamp}\n")
        file.write(f"**User:** {user_message}\n\n")
        file.write(f"**Assistant:** {assistant_response}\n")

def clear_log(user_id: str, storage: Storage = None):
    """Clear the log file after consolidation."""
    f = get_log_file(user_id, storage)
    if f.exists():
        f.unlink()

async def extract_and_store(llm_call, user_id: str, user_message: str, assistant_response: str, storage: Storage = None):
    # Always log raw conversation
    append_log(user_id, user_message, assistant_response, storage)

    # Extract facts to memory
    prompt = f"""Extract any facts, preferences, or important details worth remembering from this conversation.
Be concise but preserve important details. If nothing worth remembering, respond with "NOTHING".

User: {user_message}
Assistant: {assistant_response}

Extracted facts (markdown bullet points, or NOTHING):"""

    result = await llm_call(prompt)
    if result.strip().upper() != "NOTHING":
        append(user_id, result, storage)

async def consolidate(llm_call, user_id: str, storage: Storage = None):
    """Consolidate raw log into organized memory, then clear log."""
    log_content = read_log(user_id, storage)
    if not log_content.strip():
        return None

    existing_memory = read(user_id, storage)

    prompt = f"""You are organizing a user's conversation history into a well-structured knowledge base for Obsidian.

## Existing Memory
{existing_memory}

## New Conversation Log
{log_content}

Create an updated, well-organized markdown document with:
- Clear sections/headers for different topics (e.g., ## Preferences, ## Work, ## Family, ## Goals)
- Bullet points for facts
- Remove duplicates
- Keep it concise but preserve important details
- Use Obsidian-friendly markdown (links like [[Topic]] where appropriate)

Output the complete updated memory document:"""

    result = await llm_call(prompt)

    # Overwrite memory with consolidated version
    f = get_memory_file(user_id, storage)
    with open(f, "w") as file:
        file.write(result)

    # Clear the log
    clear_log(user_id, storage)

    return result
