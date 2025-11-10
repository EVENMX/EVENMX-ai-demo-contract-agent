from __future__ import annotations

from pathlib import Path

from .checklist_loader import ChecklistRepository
from .drive_client import DriveService
from .ingestion import EmptyDocumentError, UnsupportedFileTypeError, extract_text
from .llm_agent import ContractReviewAgent
from .models import ChecklistEvaluation, ReportArtifact, TelegramDispatchResult
from .report_generator import ReportGenerator
from .telegram_client import TelegramNotifier


class ReviewService:
    def __init__(self, checklist_repo: ChecklistRepository) -> None:
        self.repo = checklist_repo
        self.agent = ContractReviewAgent()
        self.reporter = ReportGenerator()
        self.drive = DriveService()
        self.notifier = TelegramNotifier()

    async def review_contract(
        self,
        *,
        file_path: Path,
        original_filename: str,
        section_id: str,
    ) -> tuple[ChecklistEvaluation, ReportArtifact, str, TelegramDispatchResult]:
        section = self.repo.get(section_id)
        contract_text = extract_text(file_path, original_filename)
        contract_title = _derive_contract_title(original_filename)

        evaluation = await self.agent.review(contract_text=contract_text, section=section)
        report = self.reporter.generate(contract_title=contract_title, section=section, evaluation=evaluation)
        drive_link = self.drive.upload_report(report.local_path)
        report.drive_link = drive_link
        telegram_result = await self.notifier.notify_review_complete(evaluation=evaluation)
        return evaluation, report, drive_link, telegram_result


def _derive_contract_title(filename: str) -> str:
    return Path(filename).stem.replace("_", " ").title() or "Contract"
