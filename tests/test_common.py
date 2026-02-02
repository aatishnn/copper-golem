import tempfile
import shutil
from pathlib import Path
import pytest
from src.common import Storage, sanitize_user_id
from telegram.helpers import escape_markdown

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

def test_escape_markdown_v2_special_chars():
    # Using telegram's escape_markdown with version=2
    assert escape_markdown("*bold*", version=2) == "\\*bold\\*"
    assert escape_markdown("`code`", version=2) == "\\`code\\`"
    assert escape_markdown("[link](url)", version=2) == "\\[link\\]\\(url\\)"

def test_escape_markdown_v2_preserves_alphanumeric():
    content = "User likes pizza and coffee 123"
    assert escape_markdown(content, version=2) == content
