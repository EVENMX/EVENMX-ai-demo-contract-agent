from __future__ import annotations

from datetime import datetime, timezone
from textwrap import dedent
from .models import ChecklistEvaluation, ChecklistSection, ReportArtifact


class ReportGenerator:
    def generate(
        self,
        *,
        contract_title: str,
        section: ChecklistSection,
        evaluation: ChecklistEvaluation,
    ) -> ReportArtifact:
        timestamp = datetime.now(timezone.utc)
        filename = f"{_slugify(contract_title)}-{timestamp:%Y%m%d-%H%M%S}.md"
        markdown = self._build_markdown(contract_title, section, evaluation, timestamp)

        local_path = f"in-memory://{filename}"

        return ReportArtifact(
            contract_title=contract_title,
            generated_at=timestamp,
            local_path=local_path,
            content=markdown,
            evaluation=evaluation,
        )

    def _build_markdown(
        self,
        contract_title: str,
        section: ChecklistSection,
        evaluation: ChecklistEvaluation,
        timestamp: datetime,
    ) -> str:
        counts = evaluation.status_counts()
        lines = [
            f"# Contract Review Report — {contract_title}",
            "",
            f"*Generated:* {timestamp:%Y-%m-%d %H:%M UTC}",
            f"*Jurisdiction:* {section.jurisdiction}",
            f"*Contract type:* {section.contract_type}",
            f"*Checklist version:* {section.version}",
            "",
            "## Summary",
            evaluation.summary,
            "",
            "## Status Overview",
            f"- ✅ Compliant: {counts['✅']}",
            f"- ⚠️ Needs attention: {counts['⚠️']}",
            f"- ❌ Non-compliant: {counts['❌']}",
            "",
            "## Detailed Findings",
            "| Category | Requirement | Status | Notes |",
            "| --- | --- | --- | --- |",
        ]
        for item in evaluation.items:
            lines.append(
                f"| {item.category.title()} | {item.description} | {item.status} | {item.notes.replace('|', '/')} |"
            )
        lines.append("")
        lines.append("---")
        lines.append(
            dedent(
                """
                _This is a demo artifact. Replace the markdown-generation logic with a Google Docs API
                integration to upload the report into Drive, then update the returned Drive link._
                """
            ).strip()
        )
        return "\n".join(lines)


def _slugify(value: str) -> str:
    safe = [char.lower() if char.isalnum() else "-" for char in value.strip()]
    result = "".join(safe).strip("-") or "contract"
    # Replace multiple consecutive dashes with a single dash
    while "--" in result:
        result = result.replace("--", "-")
    return result
