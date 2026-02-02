import tempfile
import shutil
from pathlib import Path
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
    from src.skills import memory
    result = memory.read("user1", storage)
    assert result == ""

def test_append_and_read(storage):
    from src.skills import memory
    memory.append("user1", "- likes pizza", storage)
    result = memory.read("user1", storage)
    assert "likes pizza" in result

def test_user_isolation(storage):
    from src.skills import memory
    memory.append("user1", "- fact for user1", storage)
    memory.append("user2", "- fact for user2", storage)

    assert "user1" in memory.read("user1", storage)
    assert "user2" in memory.read("user2", storage)
    assert "user2" not in memory.read("user1", storage)

@pytest.mark.asyncio
async def test_extract_and_store(storage):
    from src.skills import memory

    mock_llm = AsyncMock(return_value="- User likes spicy food")
    await memory.extract_and_store(mock_llm, "user1", "I love spicy food", "Got it!", storage)

    result = memory.read("user1", storage)
    assert "spicy food" in result

@pytest.mark.asyncio
async def test_extract_nothing(storage):
    from src.skills import memory

    mock_llm = AsyncMock(return_value="NOTHING")
    await memory.extract_and_store(mock_llm, "user1", "hello", "hi there", storage)

    # Memory should be empty but log should have the conversation
    result = memory.read("user1", storage)
    assert result == ""
    log = memory.read_log("user1", storage)
    assert "hello" in log
    assert "hi there" in log

def test_log_append_and_read(storage):
    from src.skills import memory
    memory.append_log("user1", "What's the weather?", "It's sunny!", storage)
    log = memory.read_log("user1", storage)
    assert "What's the weather?" in log
    assert "It's sunny!" in log

def test_wiki_dir_creates_directory(storage):
    from src.skills import memory
    wiki_dir = memory.get_wiki_dir("user1", storage)
    assert wiki_dir.exists()
    assert wiki_dir.name == "wiki"
