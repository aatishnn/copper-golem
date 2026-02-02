from pathlib import Path

DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data"

class Storage:
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or DEFAULT_DATA_DIR

    def get_user_dir(self, user_id: str) -> Path:
        user_dir = self.data_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir

    def get_all_user_ids(self) -> list[str]:
        if not self.data_dir.exists():
            return []
        return [d.name for d in self.data_dir.iterdir() if d.is_dir()]

# Default instance for production use
storage = Storage()
