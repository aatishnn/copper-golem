import tempfile
import shutil
from pathlib import Path
import pytest
from src.common import Storage

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
