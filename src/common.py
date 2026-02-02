import re
from pathlib import Path

DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data"

def sanitize_user_id(user_id: str) -> str:
    """Sanitize user_id to prevent path traversal. Allow only alphanumeric, dash, underscore."""
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', str(user_id))
    if not sanitized:
        raise ValueError("Invalid user_id")
    return sanitized

def escape_markdown(content: str) -> str:
    """Escape all markdown special characters."""
    # Characters that have special meaning in markdown
    special_chars = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!', '|', '~', '>']
    for char in special_chars:
        content = content.replace(char, '\\' + char)
    return content

class Storage:
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or DEFAULT_DATA_DIR

    def get_user_dir(self, user_id: str) -> Path:
        safe_id = sanitize_user_id(user_id)
        user_dir = self.data_dir / safe_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def get_all_user_ids(self) -> list[str]:
        if not self.data_dir.exists():
            return []
        return [d.name for d in self.data_dir.iterdir() if d.is_dir()]

# Default instance for production use
storage = Storage()
