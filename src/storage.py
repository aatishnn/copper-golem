from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

def get_user_dir(user_id: str) -> Path:
    user_dir = DATA_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir

def get_all_user_ids() -> list[str]:
    if not DATA_DIR.exists():
        return []
    return [d.name for d in DATA_DIR.iterdir() if d.is_dir()]
