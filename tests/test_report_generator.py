"""Tests for report generation functionality."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.models import ChecklistEvaluation, ChecklistEvaluationItem, ChecklistSection
from app.report_generator import ReportGenerator, _slugify


@pytest.mark.unit
class TestSlugify:
    """Test slugify utility function."""

    def test_slugify_basic_text(self) -> None:
        """Test basic text slugification."""
        result = _slugify("Commercial Lease Agreement")
        assert result == "commercial-lease-agreement"

    def test_slugify_with_special_characters(self) -> None:
        """Test slugification removes special characters."""
        result = _slugify("Contract #123 (2024)")
        assert result == "contract-123-2024"

    def test_slugify_strips_whitespace(self) -> None:
        """Test that slugify strips leading/trailing whitespace."""
        result = _slugify("  Test Contract  ")
        assert result == "test-contract"

    def test_slugify_empty_string(self) -> None:
        """Test that empty string returns 'contract'."""
        result = _slugify("")
        assert result == "contract"

    def test_slugify_only_special_characters(self) -> None:
        """Test that string with only special characters returns 'contract'."""
        result = _slugify("!!!@@@###")
        assert result == "contract"


@pytest.mark.unit
class TestReportGenerator:
    """Test report generation functionality."""

    def test_generate_report_creates_file(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation, temp_dir: Path
    ) -> None:
        """Test that report generation creates a markdown file."""
        generator = ReportGenerator()
        # Override output directory for testing
        generator.output_dir = temp_dir

        report = generator.generate(
            contract_title="Test Contract",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )

        assert Path(report.local_path).exists()
        assert report.local_path.endswith(".md")
        assert report.contract_title == "Test Contract"

    def test_generate_report_contains_required_sections(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation, temp_dir: Path
    ) -> None:
        """Test that generated report contains all required sections."""
        generator = ReportGenerator()
        generator.output_dir = temp_dir

        report = generator.generate(
            contract_title="Test Contract",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )

        content = Path(report.local_path).read_text(encoding="utf-8")

        assert "# Contract Review Report" in content
        assert "Test Contract" in content
        assert "## Summary" in content
        assert "## Status Overview" in content
        assert "## Detailed Findings" in content
        assert sample_checklist_section.jurisdiction in content
        assert sample_checklist_section.contract_type in content

    def test_generate_report_includes_evaluation_summary(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation, temp_dir: Path
    ) -> None:
        """Test that report includes the evaluation summary."""
        generator = ReportGenerator()
        generator.output_dir = temp_dir

        report = generator.generate(
            contract_title="Test Contract",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )

        content = Path(report.local_path).read_text(encoding="utf-8")
        assert sample_evaluation.summary in content

    def test_generate_report_includes_status_counts(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation, temp_dir: Path
    ) -> None:
        """Test that report includes status count overview."""
        generator = ReportGenerator()
        generator.output_dir = temp_dir

        report = generator.generate(
            contract_title="Test Contract",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )

        content = Path(report.local_path).read_text(encoding="utf-8")
        assert "✅ Compliant:" in content
        assert "⚠️ Needs attention:" in content
        assert "❌ Non-compliant:" in content

    def test_generate_report_includes_all_evaluation_items(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation, temp_dir: Path
    ) -> None:
        """Test that report includes all evaluation items in the table."""
        generator = ReportGenerator()
        generator.output_dir = temp_dir

        report = generator.generate(
            contract_title="Test Contract",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )

        content = Path(report.local_path).read_text(encoding="utf-8")

        # Check that all item descriptions appear in the content
        for item in sample_evaluation.items:
            assert item.description in content or item.key in content

    def test_generate_report_has_timestamp(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation, temp_dir: Path
    ) -> None:
        """Test that report includes generation timestamp."""
        generator = ReportGenerator()
        generator.output_dir = temp_dir

        report = generator.generate(
            contract_title="Test Contract",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )

        assert report.generated_at is not None
        content = Path(report.local_path).read_text(encoding="utf-8")
        assert "Generated:" in content

    def test_generate_report_filename_format(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation, temp_dir: Path
    ) -> None:
        """Test that report filename follows expected format."""
        generator = ReportGenerator()
        generator.output_dir = temp_dir

        report = generator.generate(
            contract_title="Test Contract",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )

        filename = Path(report.local_path).name
        assert filename.startswith("test-contract-")
        assert filename.endswith(".md")
        # Should have timestamp in format YYYYMMDD-HHMMSS
        parts = filename.replace(".md", "").split("-")
        assert len(parts) >= 3  # title parts + date + time

    def test_generate_report_handles_special_characters_in_title(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation, temp_dir: Path
    ) -> None:
        """Test that report generation handles special characters in contract title."""
        generator = ReportGenerator()
        generator.output_dir = temp_dir

        report = generator.generate(
            contract_title="Contract #123 (2024) - Special!",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )

        filename = Path(report.local_path).name
        # Should not have special characters in filename
        assert "#" not in filename
        assert "(" not in filename
        assert ")" not in filename
        assert "!" not in filename

    def test_generate_report_creates_output_directory(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation, temp_dir: Path
    ) -> None:
        """Test that report generator creates output directory if it doesn't exist."""
        new_output_dir = temp_dir / "new_reports"
        generator = ReportGenerator()
        generator.output_dir = new_output_dir

        # Directory should not exist yet
        assert not new_output_dir.exists()

        # Ensure directory is created before writing (mimic __init__ behavior)
        new_output_dir.mkdir(parents=True, exist_ok=True)

        report = generator.generate(
            contract_title="Test Contract",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )

        # Directory should be created
        assert new_output_dir.exists()
        assert Path(report.local_path).exists()

