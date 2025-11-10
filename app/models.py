from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


StatusLiteral = Literal["✅", "⚠️", "❌"]


class ChecklistSection(BaseModel):
    id: str
    jurisdiction: str
    contract_type: str
    version: str
    legal_requirements: Dict[str, Optional[str]]
    company_requirements: Dict[str, Optional[str]]
    metadata: Dict[str, Optional[str]]


class ChecklistEvaluationItem(BaseModel):
    key: str
    description: str
    status: StatusLiteral
    notes: str = Field(default_factory=str)
    category: Literal["legal", "company"]


class ChecklistEvaluation(BaseModel):
    summary: str
    items: List[ChecklistEvaluationItem]

    def top_issues(self, limit: int = 3) -> List[ChecklistEvaluationItem]:
        priority = {"❌": 0, "⚠️": 1, "✅": 2}
        return sorted(self.items, key=lambda item: (priority[item.status], item.key))[:limit]

    def status_counts(self) -> Dict[StatusLiteral, int]:
        counts: Dict[StatusLiteral, int] = {"✅": 0, "⚠️": 0, "❌": 0}
        for item in self.items:
            counts[item.status] += 1
        return counts


class ReportArtifact(BaseModel):
    contract_title: str
    generated_at: datetime
    local_path: str
    drive_link: Optional[str] = None
    evaluation: ChecklistEvaluation


class TelegramDispatchResult(BaseModel):
    sent: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
