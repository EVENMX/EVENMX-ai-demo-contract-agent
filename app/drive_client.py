from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DriveService:
    def upload_report(self, report_path: str, *, folder_override: Optional[str] = None) -> str:
        path = Path(report_path)
        if folder_override:
            logger.info("Pretending to upload %s to Drive folder %s", path.name, folder_override)
        else:
            logger.info("Pretending to upload %s to Drive (no folder configured)", path.name)
        fake_link = f"https://drive.google.com/demo/{path.stem}"
        return fake_link
