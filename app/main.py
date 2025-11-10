from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .checklist_loader import ChecklistRepository
from .config import get_settings
from .ingestion import EmptyDocumentError, UnsupportedFileTypeError
from .review_service import ReviewService

settings = get_settings()
repo = ChecklistRepository()
review_service = ReviewService(repo)

app = FastAPI(title="Contract Review Agent (Demo)")

# Determine base directory - works in both local and Vercel environments
project_root = os.environ.get("PROJECT_ROOT")
if project_root:
    _base_dir = Path(project_root)
else:
    _base_dir = Path(__file__).resolve().parent.parent

_app_dir = _base_dir / "app"
_data_dir = _app_dir / "data"
_static_dir = _base_dir / "static"
_templates_dir = _base_dir / "templates"

# Mount static files if directory exists
if _static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

# Initialize templates
if not _templates_dir.exists():
    raise RuntimeError(f"Templates directory not found at {_templates_dir}")
templates = Jinja2Templates(directory=str(_templates_dir))


@app.get("/healthz")
def healthcheck() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    sections = repo.list_sections()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "sections": sections,
            "result": None,
            "error": None,
        },
    )


@app.get("/sample-contract")
def get_sample_contract() -> JSONResponse:
    """Return the sample contract content."""
    sample_path = _data_dir / "sample_contract.txt"
    if not sample_path.exists():
        return JSONResponse({"error": "Sample contract not found"}, status_code=404)
    content = sample_path.read_text(encoding="utf-8")
    return JSONResponse({"content": content})


@app.post("/review", response_class=HTMLResponse)
async def review_contract(
    request: Request,
    checklist_section: str = Form(...),
    contract_file: UploadFile = File(None),
    contract_text: str = Form(None),
) -> HTMLResponse:
    sections = repo.list_sections()
    
    # Determine if we're using file upload or text content
    use_text = contract_text is not None and contract_text.strip()
    use_file = contract_file and contract_file.filename
    
    if not use_text and not use_file:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "sections": sections,
                "result": None,
                "error": "Please upload a contract file or provide contract text.",
            },
            status_code=400,
        )
    
    # Handle text content
    if use_text:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as buffer:
            buffer.write(contract_text)
            tmp_path = Path(buffer.name)
            original_filename = "sample_contract.txt"
    # Handle file upload
    else:
        with tempfile.NamedTemporaryFile(delete=False) as buffer:
            buffer.write(await contract_file.read())
            tmp_path = Path(buffer.name)
            original_filename = contract_file.filename or "contract.txt"

    try:
        evaluation, report, drive_link, telegram_result = await review_service.review_contract(
            file_path=tmp_path,
            original_filename=original_filename,
            section_id=checklist_section,
        )
        result = {
            "evaluation": evaluation,
            "report": report,
            "drive_link": drive_link,
            "telegram_result": telegram_result,
        }
        context = {"request": request, "sections": sections, "result": result, "error": None}
        status_code = 200
    except (UnsupportedFileTypeError, EmptyDocumentError) as exc:
        context = {"request": request, "sections": sections, "result": None, "error": str(exc)}
        status_code = 400
    except Exception as exc:  # pylint: disable=broad-except
        context = {
            "request": request,
            "sections": sections,
            "result": None,
            "error": f"Could not complete review: {exc}",
        }
        status_code = 500
    finally:
        tmp_path.unlink(missing_ok=True)

    return templates.TemplateResponse("index.html", context, status_code=status_code)
