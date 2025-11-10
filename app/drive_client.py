from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from .config import get_settings

logger = logging.getLogger(__name__)


class DriveService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def upload_report(self, report_path: str, *, folder_override: Optional[str] = None) -> str:
        path = Path(report_path)
        folder = folder_override or self.settings.google_drive_folder
        # TODO: Replace with Google Drive + Docs API integration for real uploads.
        logger.info("Pretending to upload %s to Drive folder %s", path.name, folder)
        fake_link = f"https://drive.google.com/demo/{path.stem}"
        return fake_link
