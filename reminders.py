import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

DATA_DIR = Path(__file__).parent / "data"

def get_user_dir(user_id: str) -> Path:
    user_dir = DATA_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir

def get_reminders_file(user_id: str) -> Path:
    return get_user_dir(user_id) / "reminders.md"

def read_reminders(user_id: str) -> str:
    f = get_reminders_file(user_id)
    if not f.exists():
        f.write_text("# Reminders\n\n")
    return f.read_text()

def parse_reminders(user_id: str) -> list[dict]:
    content = read_reminders(user_id)
    reminders = []
    pattern = r"- \[([ x])\] (.+?)(?:\s+`due:([^`]+)`)?(?:\s+`created:([^`]+)`)?(?:\s+`completed:([^`]+)`)?\s*$"

    for line in content.split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            reminders.append({
                "text": match.group(2).strip(),
                "completed": match.group(1) == "x",
                "due": match.group(3),
                "created": match.group(4),
                "raw": line
            })
    return reminders

def add_reminder(user_id: str, text: str, due: Optional[str] = None):
    f = get_reminders_file(user_id)
    if not f.exists():
        f.write_text("# Reminders\n\n")
    created = datetime.now().strftime("%Y-%m-%dT%H:%M")
    line = f"- [ ] {text}"
    if due:
        line += f" `due:{due}`"
    line += f" `created:{created}`"
    with open(f, "a") as file:
        file.write(f"{line}\n")

def mark_complete(user_id: str, text: str):
    f = get_reminders_file(user_id)
    content = f.read_text()
    completed_time = datetime.now().strftime("%Y-%m-%dT%H:%M")
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if text in line and "- [ ]" in line:
            lines[i] = line.replace("- [ ]", "- [x]") + f" `completed:{completed_time}`"
            break
    f.write_text("\n".join(lines))

def get_due_reminders(user_id: str) -> list[dict]:
    now = datetime.now()
    due_reminders = []
    for r in parse_reminders(user_id):
        if r["completed"] or not r["due"]:
            continue
        try:
            if datetime.fromisoformat(r["due"]) <= now:
                due_reminders.append(r)
        except ValueError:
            continue
    return due_reminders

def get_all_user_ids() -> list[str]:
    if not DATA_DIR.exists():
        return []
    return [d.name for d in DATA_DIR.iterdir() if d.is_dir()]

async def extract_and_store_reminder(llm_call, user_id: str, user_message: str):
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
        add_reminder(user_id, text, due)
        return {"text": text, "due": due}
    return None

async def reminder_loop(callback: Callable[[str, dict], None], interval: int = 60):
    """Check all users for due reminders."""
    while True:
        for user_id in get_all_user_ids():
            for r in get_due_reminders(user_id):
                await callback(user_id, r)
                mark_complete(user_id, r["text"])
        await asyncio.sleep(interval)
