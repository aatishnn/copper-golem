import asyncio
import re
from datetime import datetime
from typing import Callable, Optional
from src.common import Storage, storage as default_storage

def get_reminders_file(user_id: str, storage: Storage = None):
    s = storage or default_storage
    return s.get_user_dir(user_id) / "reminders.md"

def read(user_id: str, storage: Storage = None) -> str:
    f = get_reminders_file(user_id, storage)
    return f.read_text() if f.exists() else ""

def parse(user_id: str, storage: Storage = None) -> list[dict]:
    content = read(user_id, storage)
    reminders = []
    pattern = r"- \[([ x])\] ([^`\n]+?)(?:\s+`due:([^`]+)`)?\s*$"

    for line in content.split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            reminders.append({
                "text": match.group(2).strip(),
                "completed": match.group(1) == "x",
                "due": match.group(3),
            })
    return reminders

def add(user_id: str, text: str, due: Optional[str] = None, storage: Storage = None):
    f = get_reminders_file(user_id, storage)
    line = f"- [ ] {text}"
    if due:
        line += f" `due:{due}`"
    with open(f, "a") as file:
        file.write(f"{line}\n")

def mark_complete(user_id: str, text: str, storage: Storage = None):
    f = get_reminders_file(user_id, storage)
    if not f.exists():
        return
    content = f.read_text()
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if text in line and "- [ ]" in line:
            lines[i] = line.replace("- [ ]", "- [x]")
            break
    f.write_text("\n".join(lines))

def get_due(user_id: str, storage: Storage = None) -> list[dict]:
    now = datetime.now()
    due_reminders = []
    for r in parse(user_id, storage):
        if r["completed"] or not r["due"]:
            continue
        try:
            if datetime.fromisoformat(r["due"]) <= now:
                due_reminders.append(r)
        except ValueError:
            continue
    return due_reminders

async def extract_and_store(llm_call, user_id: str, user_message: str, storage: Storage = None):
    now = datetime.now()
    prompt = f"""Current time: {now.strftime("%Y-%m-%d %H:%M")}

Does this message contain a reminder, todo, or task to remember? If yes, extract it.
Respond in this exact format:
REMINDER: <task text>
DUE: <ISO datetime like 2024-02-01T17:00, or NONE if no specific time>

If no reminder/todo, respond with just: NONE

User message: {user_message}"""

    result = await llm_call(prompt)
    if "NONE" in result and "REMINDER:" not in result:
        return None

    reminder_match = re.search(r"REMINDER:\s*(.+?)(?:\n|$)", result)
    due_match = re.search(r"DUE:\s*(.+?)(?:\n|$)", result)

    if reminder_match:
        text = reminder_match.group(1).strip()
        due = None
        if due_match:
            due_str = due_match.group(1).strip()
            if due_str.upper() != "NONE":
                due = due_str
        add(user_id, text, due, storage)
        return {"text": text, "due": due}
    return None

async def loop(callback: Callable[[str, dict], None], interval: int = 60, storage: Storage = None):
    s = storage or default_storage
    while True:
        for user_id in s.get_all_user_ids():
            for r in get_due(user_id, storage):
                await callback(user_id, r)
                mark_complete(user_id, r["text"], storage)
        await asyncio.sleep(interval)
