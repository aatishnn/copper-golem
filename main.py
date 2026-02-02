import asyncio
from src.agent import chat
from src.skills import reminders

USER_ID = "cli"

async def on_reminder(user_id: str, reminder: dict):
    if user_id == USER_ID:
        print(f"\n🔔 REMINDER: {reminder['text']}")
        print("You: ", end="", flush=True)

async def input_loop():
    print("Assistant ready. Type 'quit' to exit.\n")

    while True:
        try:
            user_input = await asyncio.to_thread(input, "You: ")
        except EOFError:
            break

        if user_input.lower() in ("quit", "exit", "q"):
            break

        if not user_input.strip():
            continue

        response = await chat(USER_ID, user_input)
        print(f"Assistant: {response}\n")

async def main():
    reminder_task = asyncio.create_task(reminders.loop(on_reminder, interval=60))

    try:
        await input_loop()
    finally:
        reminder_task.cancel()
        try:
            await reminder_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
