"""Pytest configuration and shared fixtures."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from app.models import ChecklistEvaluation, ChecklistEvaluationItem, ChecklistSection


@pytest.fixture
def sample_checklist_data() -> dict:
    """Sample checklist data for testing."""
    return {
        "sections": [
            {
                "id": "QLD_COMMERCIAL_LEASE",
                "jurisdiction": "Queensland",
                "contract_type": "Commercial Lease",
                "version": "1.0",
                "legal_requirements": {
                    "parties_identified": "Clearly identify landlord and tenant legal entities.",
                    "premises_description": "Describe the leased premises with address.",
                    "lease_term": "State commencement, expiry, and any option periods.",
                    "rent_details": "Detail base rent, payment frequency, and method.",
                },
                "company_requirements": {
                    "minimum_notice_period_days": "Provide at least 30 days written notice.",
                    "maximum_security_deposit_months": "Security deposit must not exceed 2 months.",
                },
                "metadata": {
                    "last_updated": "2024-05-18",
                    "author": "Legal Ops Team",
                },
            }
        ]
    }


@pytest.fixture
def temp_checklist_file(sample_checklist_data: dict, tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary checklist JSON file for testing."""
    checklist_file = tmp_path / "test_checklist.json"
    checklist_file.write_text(json.dumps(sample_checklist_data, indent=2), encoding="utf-8")
    yield checklist_file
    checklist_file.unlink(missing_ok=True)


@pytest.fixture
def sample_checklist_section() -> ChecklistSection:
    """Sample checklist section for testing."""
    return ChecklistSection(
        id="QLD_COMMERCIAL_LEASE",
        jurisdiction="Queensland",
        contract_type="Commercial Lease",
        version="1.0",
        legal_requirements={
            "parties_identified": "Clearly identify landlord and tenant legal entities.",
            "premises_description": "Describe the leased premises with address.",
        },
        company_requirements={
            "minimum_notice_period_days": "Provide at least 30 days written notice.",
        },
        metadata={"last_updated": "2024-05-18", "author": "Legal Ops Team"},
    )


@pytest.fixture
def sample_evaluation() -> ChecklistEvaluation:
    """Sample evaluation result for testing."""
    return ChecklistEvaluation(
        summary="Test evaluation completed.",
        items=[
            ChecklistEvaluationItem(
                key="parties_identified",
                description="Clearly identify landlord and tenant legal entities.",
                status="✅",
                notes="Both parties clearly identified with ABNs.",
                category="legal",
            ),
            ChecklistEvaluationItem(
                key="premises_description",
                description="Describe the leased premises with address.",
                status="✅",
                notes="Premises clearly described.",
                category="legal",
            ),
            ChecklistEvaluationItem(
                key="minimum_notice_period_days",
                description="Provide at least 30 days written notice.",
                status="⚠️",
                notes="Notice period mentioned but not explicitly 30 days.",
                category="company",
            ),
        ],
    )


@pytest.fixture
def sample_contract_text() -> str:
    """Sample contract text for testing."""
    return Path(__file__).parent / "fixtures" / "sample_contract.txt"


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock environment variables for testing."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
    monkeypatch.setenv("TELEGRAM_BOSS_CHAT_ID", "")
    monkeypatch.setenv("GOOGLE_DRIVE_FOLDER", "Test_Contract_Reviews")
    monkeypatch.setenv("REPORT_STORAGE_DIR", "test_reports")

