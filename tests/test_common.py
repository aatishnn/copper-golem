import tempfile
import shutil
from pathlib import Path
import pytest
from src.common import Storage, sanitize_user_id, sanitize_for_prompt

@pytest.fixture
def storage():
    temp_dir = Path(tempfile.mkdtemp())
    s = Storage(data_dir=temp_dir)
    yield s
    shutil.rmtree(temp_dir)

def test_get_user_dir_creates_directory(storage):
    user_dir = storage.get_user_dir("testuser")
    assert user_dir.exists()
    assert user_dir.name == "testuser"

def test_get_user_dir_idempotent(storage):
    dir1 = storage.get_user_dir("testuser")
    dir2 = storage.get_user_dir("testuser")
    assert dir1 == dir2

def test_get_all_user_ids_empty(storage):
    users = storage.get_all_user_ids()
    assert users == []

def test_get_all_user_ids(storage):
    storage.get_user_dir("user1")
    storage.get_user_dir("user2")
    storage.get_user_dir("user3")

    users = storage.get_all_user_ids()
    assert set(users) == {"user1", "user2", "user3"}

# Sanitization tests

def test_sanitize_user_id_valid():
    assert sanitize_user_id("user123") == "user123"
    assert sanitize_user_id("user-name_1") == "user-name_1"
    assert sanitize_user_id("12345") == "12345"

def test_sanitize_user_id_path_traversal():
    assert sanitize_user_id("../../../etc") == "etc"
    assert sanitize_user_id("user/../admin") == "useradmin"
    assert sanitize_user_id("/etc/passwd") == "etcpasswd"

def test_sanitize_user_id_special_chars():
    assert sanitize_user_id("user@email.com") == "useremailcom"
    assert sanitize_user_id("user name") == "username"

def test_sanitize_user_id_empty_raises():
    with pytest.raises(ValueError):
        sanitize_user_id("...")
    with pytest.raises(ValueError):
        sanitize_user_id("///")

def test_sanitize_for_prompt_headers():
    content = "# Injected Header\n## Another"
    sanitized = sanitize_for_prompt(content)
    assert not sanitized.startswith("# ")
    assert "\\# Injected" in sanitized

def test_sanitize_for_prompt_code_blocks():
    content = "```python\nmalicious code\n```"
    sanitized = sanitize_for_prompt(content)
    assert "```" not in sanitized

def test_sanitize_for_prompt_preserves_normal_text():
    content = "User likes pizza and coffee"
    assert sanitize_for_prompt(content) == content
