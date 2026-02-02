import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import AsyncMock
import pytest
from src.common import Storage

@pytest.fixture
def storage():
    temp_dir = Path(tempfile.mkdtemp())
    s = Storage(data_dir=temp_dir)
    yield s
    shutil.rmtree(temp_dir)

def test_read_empty(storage):
    from src.skills import reminders
    result = reminders.read("user1", storage)
    assert result == ""

def test_add_reminder(storage):
    from src.skills import reminders
    reminders.add("user1", "call mom", "2024-02-01T17:00", storage)
    result = reminders.read("user1", storage)
    assert "call mom" in result
    assert "due:2024-02-01T17:00" in result

def test_add_reminder_no_due(storage):
    from src.skills import reminders
    reminders.add("user1", "buy milk", None, storage)
    result = reminders.read("user1", storage)
    assert "buy milk" in result
    assert "due:" not in result

def test_parse_reminders(storage):
    from src.skills import reminders
    reminders.add("user1", "task1", "2024-02-01T10:00", storage)
    reminders.add("user1", "task2", None, storage)

    parsed = reminders.parse("user1", storage)
    assert len(parsed) == 2
    assert parsed[0]["text"] == "task1"
    assert parsed[0]["due"] == "2024-02-01T10:00"
    assert parsed[0]["completed"] == False
    assert parsed[1]["text"] == "task2"
    assert parsed[1]["due"] is None

def test_mark_complete(storage):
    from src.skills import reminders
    reminders.add("user1", "do laundry", None, storage)

    parsed_before = reminders.parse("user1", storage)
    assert parsed_before[0]["completed"] == False

    reminders.mark_complete("user1", "do laundry", storage)

    parsed_after = reminders.parse("user1", storage)
    assert parsed_after[0]["completed"] == True

def test_get_due(storage):
    from src.skills import reminders
    past = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M")
    future = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")

    reminders.add("user1", "past task", past, storage)
    reminders.add("user1", "future task", future, storage)

    due = reminders.get_due("user1", storage)
    assert len(due) == 1
    assert due[0]["text"] == "past task"

def test_user_isolation(storage):
    from src.skills import reminders
    reminders.add("user1", "user1 task", None, storage)
    reminders.add("user2", "user2 task", None, storage)

    assert "user1 task" in reminders.read("user1", storage)
    assert "user2 task" in reminders.read("user2", storage)
    assert "user2 task" not in reminders.read("user1", storage)

@pytest.mark.asyncio
async def test_extract_and_store(storage):
    from src.skills import reminders

    mock_llm = AsyncMock(return_value="REMINDER: call dentist\nDUE: 2024-02-01T14:00")
    result = await reminders.extract_and_store(mock_llm, "user1", "remind me to call dentist tomorrow at 2pm", storage)

    assert result["text"] == "call dentist"
    assert result["due"] == "2024-02-01T14:00"
    assert "call dentist" in reminders.read("user1", storage)

@pytest.mark.asyncio
async def test_extract_none(storage):
    from src.skills import reminders

    mock_llm = AsyncMock(return_value="NONE")
    result = await reminders.extract_and_store(mock_llm, "user1", "hello there", storage)

    assert result is None
    assert reminders.read("user1", storage) == ""
