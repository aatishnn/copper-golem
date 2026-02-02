# Copper Golem

A simple personal assistant that remembers things and sends reminders.

Inspired by [OpenClaw](https://openclaw.ai/) - but too afraid to install it, so I built a minimal POC of my own.

## Quick Start

```bash
cp .env.example .env
# Edit .env with your API keys
make run
```

## Setup

### 1. Get an OpenRouter API key

Sign up at https://openrouter.ai and get an API key.

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your keys:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Optional: Use a local LLM API instead of OpenRouter
# LLM_BASE_URL=http://192.168.1.142:4000
```

#### LLM Configuration

By default, the app uses OpenRouter's API. You can override this with the `LLM_BASE_URL` environment variable:

- **Production** (default): `https://openrouter.ai/api/v1` (OpenRouter)
- **Local Development**: `http://192.168.1.142:4000` (LM Studio, Ollama, or similar local LLM server)

### 3. Run with Docker (recommended)

```bash
make run
```

### 4. Or run locally

```bash
pip install -r requirements.txt
python main.py
```

## Telegram Bot

1. Message @BotFather on Telegram to create a bot
2. Copy the token it gives you
3. Add it to your `.env` file
4. Run:

```bash
make bot
```

## Usage

Just chat naturally:

```
You: Remember that I'm allergic to shellfish
Assistant: Got it, I'll remember that you're allergic to shellfish.

You: Remind me to call the dentist tomorrow at 2pm
Assistant: I'll remind you to call the dentist tomorrow at 2pm.

You: What do you know about me?
Assistant: I know you're allergic to shellfish.
```

## Data

Each user gets their own folder in `./data/<user_id>/`:

- `memory.md` - facts and details about you
- `reminders.md` - active and completed reminders

You can edit these files directly if needed.

## Make Commands

- `make run` - Start CLI chat (alternative to Bot UI)
- `make bot` - Start Telegram bot
- `make shell` - Open shell in container
- `make clean` - Remove container and data
