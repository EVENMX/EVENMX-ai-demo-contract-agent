from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, List

from .models import ChecklistSection


class ChecklistRepository:
    def __init__(self, checklist_path: str | None = None) -> None:
        # Determine base directory - works in both local and Vercel environments
        if checklist_path:
            self.path = Path(checklist_path)
            print(f"=== DEBUG ChecklistRepository: Using provided path: {self.path}", file=sys.stderr)
        else:
            # Try to use PROJECT_ROOT env var (set in Vercel), otherwise use relative path
            project_root = os.environ.get("PROJECT_ROOT")
            if project_root:
                base_dir = Path(project_root) / "app"
                print(f"=== DEBUG ChecklistRepository: Using PROJECT_ROOT/app: {base_dir}", file=sys.stderr)
            else:
                base_dir = Path(__file__).resolve().parent
                print(f"=== DEBUG ChecklistRepository: Using __file__ parent: {base_dir}", file=sys.stderr)
            self.path = base_dir / "data" / "contract_checklist.json"
            print(f"=== DEBUG ChecklistRepository: Looking for checklist at: {self.path}", file=sys.stderr)
        
        print(f"=== DEBUG ChecklistRepository: File exists: {self.path.exists()}", file=sys.stderr)
        if not self.path.exists():
            print(f"=== ERROR ChecklistRepository: File not found!", file=sys.stderr)
            print(f"  - Path: {self.path}", file=sys.stderr)
            print(f"  - Current dir: {Path.cwd()}", file=sys.stderr)
            print(f"  - __file__: {Path(__file__)}", file=sys.stderr)
            print(f"  - PROJECT_ROOT env: {os.environ.get('PROJECT_ROOT')}", file=sys.stderr)
            raise FileNotFoundError(f"Checklist file not found at {self.path}. Current dir: {Path.cwd()}")
        
        print(f"=== DEBUG ChecklistRepository: Loading sections...", file=sys.stderr)
        self._sections = self._load_sections()
        print(f"=== DEBUG ChecklistRepository: Loaded {len(self._sections)} sections", file=sys.stderr)

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
