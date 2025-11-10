from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .models import ChecklistSection


class ChecklistRepository:
    def __init__(self, checklist_path: str | None = None) -> None:
        # Determine base directory - works in both local and Vercel environments
        base_dir = Path(__file__).parent.parent
        if checklist_path is None:
            checklist_path = str(base_dir / "contract_checklist.json")
        self.path = Path(checklist_path)
        if not self.path.exists():
            raise FileNotFoundError(f"Checklist file not found at {self.path}")
        self._sections = self._load_sections()

    def _load_sections(self) -> Dict[str, ChecklistSection]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        sections = data.get("sections", [])
        loaded: Dict[str, ChecklistSection] = {}
        for raw_section in sections:
            section = ChecklistSection(**raw_section)
            loaded[section.id] = section
        return loaded

    def list_sections(self) -> List[ChecklistSection]:
        return list(self._sections.values())

    def get(self, section_id: str) -> ChecklistSection:
        if section_id not in self._sections:
            raise KeyError(f"Checklist section '{section_id}' not found")
        return self._sections[section_id]
