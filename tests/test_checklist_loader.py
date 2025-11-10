"""Tests for checklist loading functionality."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.checklist_loader import ChecklistRepository
from app.models import ChecklistSection


@pytest.mark.unit
class TestChecklistRepository:
    """Test checklist repository functionality."""

    def test_load_checklist_from_file(self, temp_checklist_file: Path) -> None:
        """Test loading checklist sections from a JSON file."""
        repo = ChecklistRepository(str(temp_checklist_file))
        sections = repo.list_sections()

        assert len(sections) == 1
        assert sections[0].id == "QLD_COMMERCIAL_LEASE"
        assert sections[0].jurisdiction == "Queensland"
        assert sections[0].contract_type == "Commercial Lease"

    def test_get_section_by_id(self, temp_checklist_file: Path) -> None:
        """Test retrieving a specific section by ID."""
        repo = ChecklistRepository(str(temp_checklist_file))
        section = repo.get("QLD_COMMERCIAL_LEASE")

        assert isinstance(section, ChecklistSection)
        assert section.id == "QLD_COMMERCIAL_LEASE"
        assert "parties_identified" in section.legal_requirements
        assert "minimum_notice_period_days" in section.company_requirements

    def test_get_nonexistent_section_raises_error(self, temp_checklist_file: Path) -> None:
        """Test that getting a non-existent section raises KeyError."""
        repo = ChecklistRepository(str(temp_checklist_file))

        with pytest.raises(KeyError, match="Checklist section 'INVALID_ID' not found"):
            repo.get("INVALID_ID")

    def test_list_sections_returns_all_sections(self, temp_dir: Path) -> None:
        """Test that list_sections returns all loaded sections."""
        # Create a checklist with multiple sections
        multi_section_data = {
            "sections": [
                {
                    "id": "SECTION_1",
                    "jurisdiction": "QLD",
                    "contract_type": "Type A",
                    "version": "1.0",
                    "legal_requirements": {},
                    "company_requirements": {},
                    "metadata": {},
                },
                {
                    "id": "SECTION_2",
                    "jurisdiction": "NSW",
                    "contract_type": "Type B",
                    "version": "1.0",
                    "legal_requirements": {},
                    "company_requirements": {},
                    "metadata": {},
                },
            ]
        }
        checklist_file = temp_dir / "multi_checklist.json"
        checklist_file.write_text(json.dumps(multi_section_data), encoding="utf-8")

        repo = ChecklistRepository(str(checklist_file))
        sections = repo.list_sections()

        assert len(sections) == 2
        assert {s.id for s in sections} == {"SECTION_1", "SECTION_2"}

    def test_checklist_file_not_found_raises_error(self, temp_dir: Path) -> None:
        """Test that missing checklist file raises FileNotFoundError."""
        nonexistent_file = temp_dir / "nonexistent.json"

        with pytest.raises(FileNotFoundError, match="Checklist file not found"):
            ChecklistRepository(str(nonexistent_file))

    def test_checklist_section_has_all_required_fields(self, temp_checklist_file: Path) -> None:
        """Test that loaded sections have all required fields."""
        repo = ChecklistRepository(str(temp_checklist_file))
        section = repo.get("QLD_COMMERCIAL_LEASE")

        assert hasattr(section, "id")
        assert hasattr(section, "jurisdiction")
        assert hasattr(section, "contract_type")
        assert hasattr(section, "version")
        assert hasattr(section, "legal_requirements")
        assert hasattr(section, "company_requirements")
        assert hasattr(section, "metadata")

    def test_checklist_section_requirements_are_dicts(self, temp_checklist_file: Path) -> None:
        """Test that legal and company requirements are properly loaded as dicts."""
        repo = ChecklistRepository(str(temp_checklist_file))
        section = repo.get("QLD_COMMERCIAL_LEASE")

        assert isinstance(section.legal_requirements, dict)
        assert isinstance(section.company_requirements, dict)
        assert len(section.legal_requirements) > 0
        assert len(section.company_requirements) > 0

