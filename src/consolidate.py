"""Consolidate conversation logs into organized memory for all users."""
import asyncio
from src.agent import llm_call
from src.skills import memory
from src.common import storage

async def main():
    user_ids = storage.get_all_user_ids()
    if not user_ids:
        print("No users found.")
        return

    for user_id in user_ids:
        log_content = memory.read_log(user_id)
        if not log_content.strip():
            print(f"[{user_id}] No new logs to consolidate.")
            continue

        print(f"[{user_id}] Consolidating...")
        result = await memory.consolidate(llm_call, user_id)
        if result:
            print(f"[{user_id}] Done. Memory updated.")

if __name__ == "__main__":
    asyncio.run(main())
