"""Tests for report generation functionality."""
from __future__ import annotations

import pytest

from app.models import ChecklistEvaluation, ChecklistEvaluationItem, ChecklistSection, ReportArtifact
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

    def _generate_report(
        self,
        *,
        contract_title: str,
        section: ChecklistSection,
        evaluation: ChecklistEvaluation,
    ) -> tuple[ReportArtifact, str, ChecklistEvaluation]:
        generator = ReportGenerator()
        report = generator.generate(
            contract_title=contract_title,
            section=section,
            evaluation=evaluation,
        )
        return report, report.content, evaluation

    def test_generate_report_returns_in_memory_artifact(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation
    ) -> None:
        """Ensure reports are kept in-memory to avoid filesystem writes."""
        report, _, _ = self._generate_report(
            contract_title="Test Contract",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )

        assert report.local_path.startswith("in-memory://")
        assert report.local_path.endswith(".md")
        assert report.contract_title == "Test Contract"
        assert report.content  # markdown string should not be empty

    def test_generate_report_contains_required_sections(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation
    ) -> None:
        """Generated markdown includes the core sections."""
        _, content, _ = self._generate_report(
            contract_title="Test Contract",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )

        assert "# Contract Review Report" in content
        assert "Test Contract" in content
        assert "## Summary" in content
        assert "## Status Overview" in content
        assert "## Detailed Findings" in content
        assert sample_checklist_section.jurisdiction in content
        assert sample_checklist_section.contract_type in content

    def test_generate_report_includes_evaluation_summary(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation
    ) -> None:
        """Report mirrors the evaluation summary text."""
        _, content, evaluation = self._generate_report(
            contract_title="Test Contract",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )
        assert evaluation.summary in content

    def test_generate_report_includes_status_counts(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation
    ) -> None:
        """Status overview block is rendered."""
        _, content, _ = self._generate_report(
            contract_title="Test Contract",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )
        assert "✅ Compliant:" in content
        assert "⚠️ Needs attention:" in content
        assert "❌ Non-compliant:" in content

    def test_generate_report_includes_all_evaluation_items(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation
    ) -> None:
        """Every evaluation item appears in the table."""
        _, content, evaluation = self._generate_report(
            contract_title="Test Contract",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )
        for item in evaluation.items:
            assert item.description in content or item.key in content

    def test_generate_report_has_timestamp(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation
    ) -> None:
        """Reports include a human-friendly timestamp."""
        report, content, _ = self._generate_report(
            contract_title="Test Contract",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )

        assert report.generated_at is not None
        assert "Generated:" in content

    def test_generate_report_filename_format(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation
    ) -> None:
        """The virtual filename retains the slugged title and timestamp."""
        report, _, _ = self._generate_report(
            contract_title="Test Contract",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )

        filename = report.local_path.split("://", maxsplit=1)[-1]
        assert filename.startswith("test-contract-")
        assert filename.endswith(".md")
        parts = filename.replace(".md", "").split("-")
        assert len(parts) >= 3  # title parts + date + time

    def test_generate_report_handles_special_characters_in_title(
        self, sample_checklist_section: ChecklistSection, sample_evaluation: ChecklistEvaluation
    ) -> None:
        """Slugification removes characters that would break filenames."""
        report, _, _ = self._generate_report(
            contract_title="Contract #123 (2024) - Special!",
            section=sample_checklist_section,
            evaluation=sample_evaluation,
        )

        filename = report.local_path.split("://", maxsplit=1)[-1]
        assert "#" not in filename
        assert "(" not in filename
        assert ")" not in filename
        assert "!" not in filename
