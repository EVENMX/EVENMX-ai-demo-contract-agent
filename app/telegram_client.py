from __future__ import annotations

import logging
from typing import Iterable

import httpx

from .config import get_settings
from .models import ChecklistEvaluation, TelegramDispatchResult

logger = logging.getLogger(__name__)

TELEGRAM_URL_TEMPLATE = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramNotifier:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def notify_review_complete(self, *, evaluation: ChecklistEvaluation) -> TelegramDispatchResult:
        """Send a notification that contract review is complete with summary."""
        if not self.settings.telegram_bot_token or not self.settings.telegram_boss_chat_id:
            message = "Telegram credentials missing; skipped notification."
            logger.info(message)
            logger.info("To enable Telegram, set TELEGRAM_BOT_TOKEN and TELEGRAM_BOSS_CHAT_ID in .env and restart the server.")
            return TelegramDispatchResult(sent=False, error=message)

        message_body = self._build_review_notification(evaluation)
        payload = {
            "chat_id": self.settings.telegram_boss_chat_id,
            "text": message_body,
        }
        url = TELEGRAM_URL_TEMPLATE.format(token=self.settings.telegram_bot_token)

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                message_id = data.get("result", {}).get("message_id")
                return TelegramDispatchResult(sent=True, message_id=str(message_id))
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Telegram notification failed: %s", exc)
            return TelegramDispatchResult(sent=False, error=str(exc))

    def _build_review_notification(self, evaluation: ChecklistEvaluation) -> str:
        """Build the notification message with critical issues and clause counts."""
        status_counts = evaluation.status_counts()
        compliant_count = status_counts["✅"]
        needs_review_count = status_counts["⚠️"] + status_counts["❌"]
        critical_count = status_counts["❌"]

        message_parts = ["Boss, there is a new contract review."]

        # Add critical issues if any
        if critical_count > 0:
            critical_issues = [item for item in evaluation.items if item.status == "❌"]
            if critical_issues:
                message_parts.append("\n⚠️ Critical issues found:")
                # Add first critical issue as bullet point
                first_critical = critical_issues[0]
                message_parts.append(f"• {first_critical.description}")

        # Add clause counts
        message_parts.append(f"\n📊 {compliant_count} clauses compliant, {needs_review_count} need review")

        return "\n".join(message_parts)

    async def send_summary(
        self,
        *,
        evaluation: ChecklistEvaluation,
        contract_title: str,
        drive_link: str,
    ) -> TelegramDispatchResult:
        if not self.settings.telegram_bot_token or not self.settings.telegram_boss_chat_id:
            message = "Telegram credentials missing; skipped notification."
            logger.info(message)
            logger.info("To enable Telegram, set TELEGRAM_BOT_TOKEN and TELEGRAM_BOSS_CHAT_ID in .env and restart the server.")
            return TelegramDispatchResult(sent=False, error=message)

        message_body = self._build_message(contract_title, evaluation, drive_link)
        payload = {
            "chat_id": self.settings.telegram_boss_chat_id,
            "text": message_body,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False,
        }
        url = TELEGRAM_URL_TEMPLATE.format(token=self.settings.telegram_bot_token)

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                message_id = data.get("result", {}).get("message_id")
                return TelegramDispatchResult(sent=True, message_id=str(message_id))
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Telegram notification failed: %s", exc)
            return TelegramDispatchResult(sent=False, error=str(exc))

    def _build_message(self, contract_title: str, evaluation: ChecklistEvaluation, drive_link: str) -> str:
        top_issues = evaluation.top_issues()
        bullets: Iterable[str] = (
            f"• {item.description} — {item.status} {item.notes or ''}".strip()
            for item in top_issues
        )
        bullet_text = "\n".join(bullets) or "• No major findings."
        return (
            f"Contract Review Complete ✅\n"
            f"Contract: {contract_title}\n"
            f"Main Findings:\n{bullet_text}\n\n"
            "Would you like me to communicate anything to the responsible person?\n\n"
            f"🔗 [View Full Report]({drive_link})"
        )
