# Contract Review Agent (Demo)

Python FastAPI prototype that ingests a contract file, compares it against a jurisdiction-specific checklist, generates a Markdown report (standing in for a Google Doc upload), and drafts the Telegram summary message for the boss.

## Features

- Upload PDF / DOCX / TXT contracts via simple web UI.
- Load structured requirements from `app/data/contract_checklist.json`.
- Call OpenRouter (`openai/gpt-4.1-mini`) for detailed evaluations, with a heuristic fallback when the API key is missing/offline.
- Generate Markdown output in-memory and return a fake Google Drive link placeholder.
- Prepare the Telegram notification payload; send it for real once credentials are configured.
- **Vercel-ready**: Deploy to Vercel serverless platform with proper file path handling.

## Deployment

📦 **Deploy to Vercel**: See [VERCEL_DEPLOY.md](./VERCEL_DEPLOY.md) and [VERCEL_SETUP.md](./VERCEL_SETUP.md) for complete deployment instructions and troubleshooting.

## Quickstart

1. **Install dependencies**

   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables** (create `.env`)

   ```env
   OPENROUTER_API_KEY=sk-or-...
   OPENROUTER_MODEL=openai/gpt-4.1-mini
   TELEGRAM_BOT_TOKEN=123456:ABC
   TELEGRAM_BOSS_CHAT_ID=987654321
   ```

   Leave tokens blank while testing to stay on the heuristic fallback.

3. **Run the web UI**

   ```bash
   uvicorn app.main:app --reload
   ```

   Then open http://127.0.0.1:8000 and upload a contract.

## Implementing the full integrations

- **Google Drive + Docs**: replace `DriveService.upload_report` with Drive API calls that create `/Contract_Reviews/{date}/`, upload the generated doc (or build it directly via Docs API), and return the shared link.
- **Telegram**: the notifier already posts to the Bot API when `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set; extend it to handle follow-up replies from the boss.
- **LLM prompts**: adjust `app/llm_agent.py` to include retrieval-augmented snippets or to work with your preferred agent stack (LangChain, LlamaIndex, Autogen, etc.).
- **Document parsing**: `app/ingestion.py` currently covers PDFs via pdfplumber and DOCX via python-docx; add OCR or Google Drive export for Google Docs support.

## Testing

### Local Testing

- Drop sample contracts in `./samples` (create as needed) and use the Residential vs Commercial checklist options to see different outputs.
- The Telegram + Drive steps will gracefully log warnings until credentials are supplied, so the end-to-end UI remains usable in a demo environment.

### Run Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Test on Vercel Locally

```bash
# Install Vercel CLI
npm i -g vercel

# Run locally (simulates Vercel environment)
vercel dev
```

## Project Structure

```
.
├── api/
│   └── index.py              # Vercel serverless function entry point
├── app/
│   ├── checklist_loader.py   # Loads contract checklist
│   ├── config.py             # Configuration and settings
│   ├── data/
│   │   ├── contract_checklist.json  # Contract requirements
│   │   └── sample_contract.txt      # Sample for testing
│   ├── drive_client.py       # Google Drive integration
│   ├── ingestion.py          # Document parsing (PDF, DOCX, TXT)
│   ├── llm_agent.py          # OpenRouter LLM integration
│   ├── main.py               # FastAPI application
│   ├── models.py             # Data models
│   ├── report_generator.py   # Markdown report generation
│   ├── review_service.py     # Main contract review logic
│   └── telegram_client.py    # Telegram bot integration
├── static/
│   └── styles.css            # Web UI styles
├── templates/
│   ├── base.html             # Base template
│   └── index.html            # Main UI template
├── tests/                    # Test suite
├── vercel.json               # Vercel configuration
├── .vercelignore             # Files to exclude from deployment
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── VERCEL_DEPLOY.md          # Deployment guide
└── VERCEL_SETUP.md           # Setup & troubleshooting guide
```
