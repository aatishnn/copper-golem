import json
import re
from pathlib import Path
from telegram.helpers import escape_markdown

DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data"
CONFIG_FILE = Path(__file__).parent.parent / "config.json"

# Re-export escape_markdown from telegram.helpers
__all__ = ['escape_markdown', 'sanitize_user_id', 'Storage', 'storage', 'config']

def load_config() -> dict:
    """Load config from config.json."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {"models": {}}

config = load_config()

def sanitize_user_id(user_id: str) -> str:
    """Sanitize user_id to prevent path traversal. Allow only alphanumeric, dash, underscore."""
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', str(user_id))
    if not sanitized:
        raise ValueError("Invalid user_id")
    return sanitized

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
