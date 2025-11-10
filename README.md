# Contract Review Agent (Demo)

Python FastAPI prototype that ingests a contract file, compares it against a jurisdiction-specific checklist, generates a Markdown report (standing in for a Google Doc upload), and drafts the Telegram summary message for the boss.

## Features

- Upload PDF / DOCX / TXT contracts via simple web UI.
- Load structured requirements from `contract_checklist.json`.
- Call OpenRouter (`openai/gpt-4.1-mini`) for detailed evaluations, with a heuristic fallback when the API key is missing/offline.
- Generate Markdown output in-memory and return a fake Google Drive link placeholder.
- Prepare the Telegram notification payload; send it for real once credentials are configured.

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
   TELEGRAM_CHAT_ID=987654321
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

## Testing notes

- Drop sample contracts in `./samples` (create as needed) and use the Residential vs Commercial checklist options to see different outputs.
- The Telegram + Drive steps will gracefully log warnings until credentials are supplied, so the end-to-end UI remains usable in a demo environment.
