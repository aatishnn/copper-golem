"""Consolidate conversation logs into an Obsidian wiki for all users."""
import asyncio
import json
import re
from src.agent import llm_call
from src.skills import memory
from src.common import storage

async def consolidation_llm_call(prompt: str) -> str:
    """LLM call using consolidation model."""
    return await llm_call(prompt, "consolidation")

async def get_wiki_plan(log_content: str, memory_content: str) -> dict:
    """Phase 1: Get organization plan from LLM."""
    prompt = f"""Analyze this conversation log and suggest how to organize it into an Obsidian wiki.

## Conversation Log (user's actual words)
{log_content}

## Memory Notes (our interpretation)
{memory_content}

Create topic files that organize the user's thoughts. For each file, include the user's EXACT quotes from the log.
These are their personal thoughts - preserve their words exactly.

Output as JSON (no markdown code blocks, just raw JSON):
{{
  "files": [
    {{
      "filename": "topic-name.md",
      "title": "Topic Name",
      "quotes": ["exact quote from user 1", "exact quote from user 2"]
    }}
  ]
}}

Rules:
- Use lowercase-with-dashes for filenames
- Only include files if there's meaningful content
- Quotes must be the user's exact words from the log
- Group related thoughts together
- Common topics: work, family, health, hobbies, goals, ideas, etc."""

    result = await consolidation_llm_call(prompt)

    # Extract JSON from response (handle markdown code blocks)
    json_match = re.search(r'\{[\s\S]*\}', result)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            return {"files": []}
    return {"files": []}

def generate_wiki_file(title: str, quotes: list[str]) -> str:
    """Generate Obsidian-friendly markdown content."""
    content = f"# {title}\n\n"
    for quote in quotes:
        content += f"- {quote}\n"
    return content

async def consolidate_user(user_id: str):
    """Consolidate a single user's logs into wiki."""
    log_content = memory.read_log(user_id)
    memory_content = memory.read(user_id)

    if not log_content.strip():
        return None

    # Phase 1: Get organization plan
    plan = await get_wiki_plan(log_content, memory_content)

    if not plan.get("files"):
        return None

    # Phase 2: Generate wiki files
    wiki_dir = memory.get_wiki_dir(user_id)

    created_files = []
    for file_info in plan["files"]:
        filename = file_info.get("filename", "").strip()
        title = file_info.get("title", "").strip()
        quotes = file_info.get("quotes", [])

        if not filename or not quotes:
            continue

        # Ensure .md extension
        if not filename.endswith(".md"):
            filename += ".md"

        content = generate_wiki_file(title, quotes)

        file_path = wiki_dir / filename
        with open(file_path, "w") as f:
            f.write(content)

        created_files.append(filename)

    return created_files

def get_wiki_tree(user_id: str) -> str:
    """Generate ASCII tree of wiki directory."""
    wiki_dir = memory.get_wiki_dir(user_id)
    files = sorted(wiki_dir.glob("*.md"))

    if not files:
        return "📁 wiki/\n└── (empty)"

    lines = ["📁 wiki/"]
    for i, f in enumerate(files):
        # Count notes in file
        content = f.read_text()
        note_count = content.count("- ")

        prefix = "└── " if i == len(files) - 1 else "├── "
        lines.append(f"{prefix}{f.name} ({note_count} notes)")

    return "\n".join(lines)

async def consolidate_and_tree(user_id: str) -> str:
    """Consolidate and return ASCII tree."""
    files = await consolidate_user(user_id)

    if files is None:
        return "No notes to organize yet."

    tree = get_wiki_tree(user_id)
    return f"✅ Notes organized!\n\n{tree}"

async def main():
    user_ids = storage.get_all_user_ids()
    if not user_ids:
        print("No users found.")
        return

    for user_id in user_ids:
        log_content = memory.read_log(user_id)
        if not log_content.strip():
            print(f"[{user_id}] No logs to process.")
            continue

        print(f"[{user_id}] Consolidating...")
        files = await consolidate_user(user_id)
        if files:
            print(f"[{user_id}] Created wiki files: {', '.join(files)}")
        else:
            print(f"[{user_id}] No wiki files created.")

if __name__ == "__main__":
    asyncio.run(main())
