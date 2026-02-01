# OpenClaw Agent

An intelligent AI agent that runs on WSL (Windows Subsystem for Linux) with dual-model architecture and WhatsApp integration.

## Architecture

- **Local Model**: Ollama (Llama 3.2) - For quick, simple tasks
- **Cloud Model**: Google Gemini - For complex reasoning and heavy lifting
- **Chat Channel**: WhatsApp (via whatsapp-web.js)

## Prerequisites

### On Windows (Host)
1. WSL2 installed and configured
2. Docker Desktop (optional, for containerized deployment)

### On WSL
1. Node.js 18+ or Python 3.10+
2. Ollama installed locally
3. Google Cloud credentials for Gemini API

## Quick Start (Step by Step)

### 1. Open WSL Terminal

Open PowerShell or Command Prompt and run:
```cmd
wsl
```

### 2. Clone or Copy the Project

If using git:
```bash
cd ~
git clone <your-repo-url> openclaw
cd openclaw/base-conf
```

Or if you copied the files manually, navigate to the project:
```bash
cd /path/to/base-conf
```

### 3. Run the Installation Script

This installs all dependencies (Node.js, Python, Ollama, Chromium) and sets up the Python virtual environment:
```bash
bash scripts/install-wsl.sh
```

The script will:
- Install system dependencies (Node.js, Python, Ollama, Chromium)
- Create a Python virtual environment in `./venv`
- Install all Python packages from `pyproject.toml`
- Make all scripts executable

**Note:** If you only need to set up Python (e.g., dependencies already installed):
```bash
bash scripts/setup-python.sh
```

### 4. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit the `.env` file and add your Gemini API key:
```bash
nano .env
```

Update this line with your actual API key:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

Save and exit (Ctrl+X, then Y, then Enter).

### 5. Pull the Ollama Model

The first time, you need to download the Llama 3.2 model:
```bash
ollama pull llama3.2
```

### 6. Start the Agent

```bash
./start.sh
```

### 7. Connect WhatsApp

When the agent starts, a QR code will appear in the terminal. Scan it with your WhatsApp mobile app:
1. Open WhatsApp on your phone
2. Go to Settings → Linked Devices → Link a Device
3. Scan the QR code shown in the terminal

Once connected, you can send messages to the linked WhatsApp and the agent will respond!

## Commands

While chatting with the agent via WhatsApp, you can use these commands:

| Command | Description |
|---------|-------------|
| `/clear` | Clear conversation history |
| `/status` | Show agent status and model info |
| `/model ollama <message>` | Force use Ollama for this message |
| `/model gemini <message>` | Force use Gemini for this message |

## Project Structure

```
base-conf/
├── src/
│   ├── agent/           # Core agent logic
│   ├── models/          # Model adapters (Ollama, Gemini)
│   ├── channels/        # Chat channels (WhatsApp)
│   └── utils/           # Utility functions
├── config/              # Configuration files
├── scripts/             # Startup and utility scripts
├── tests/               # Test files
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
├── package.json         # Node.js dependencies (for WhatsApp)
└── start.sh            # Main startup script
```

## Configuration

All configuration is done via the `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model to use |
| `GEMINI_API_KEY` | - | Your Google Gemini API key |
| `GEMINI_MODEL` | `gemini-1.5-pro` | Gemini model to use |
| `COMPLEXITY_THRESHOLD` | `500` | Score threshold to switch to Gemini |
| `GEMINI_TRIGGER_KEYWORDS` | `analyze\|generate code\|...` | Pipe-separated keywords that trigger Gemini |
| `LOG_LEVEL` | `info` | Logging level (debug/info/warn/error) |

## Model Selection Logic

The agent automatically selects the appropriate model based on:
- **Ollama (Local)**: Simple queries, quick responses, privacy-sensitive data
- **Gemini (Cloud)**: Complex reasoning, code generation, long context tasks

The selection is based on:
1. Message length and complexity
2. Presence of trigger keywords (analyze, generate code, complex, etc.)
3. Technical content (code blocks, etc.)
4. Conversation context length

## Troubleshooting

### Ollama not starting
```bash
# Start Ollama manually
ollama serve
```

### WhatsApp QR code not showing
```bash
# Delete old session and restart
rm -rf data/whatsapp-session
./start.sh
```

### Permission denied on start.sh
```bash
chmod +x start.sh
```

## License

MIT
