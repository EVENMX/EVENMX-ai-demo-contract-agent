from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Dict, Iterable

import httpx

from .config import get_settings
from .models import ChecklistEvaluation, ChecklistEvaluationItem, ChecklistSection

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class ContractReviewAgent:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._fallback_engine = HeuristicFallbackEngine()

    async def review(self, *, contract_text: str, section: ChecklistSection) -> ChecklistEvaluation:
        if not self.settings.openrouter_api_key:
            logger.warning("OPENROUTER_API_KEY not provided. Using heuristic fallback evaluation.")
            logger.info("To use LLM, set OPENROUTER_API_KEY in .env file and restart the server.")
            return self._fallback_engine.evaluate(contract_text=contract_text, section=section, reason="missing_api_key")
        
        logger.info(f"Using LLM model: {self.settings.openrouter_model}")

        prompt = _build_prompt(contract_text=contract_text, section=section)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
        }
        payload = {
            "model": self.settings.openrouter_model,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": "You are a contract compliance analyst. Always return valid JSON as instructed.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        }

        try:
            logger.info("Calling OpenRouter API...")
            async with httpx.AsyncClient(timeout=90) as client:
                response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                message = data["choices"][0]["message"]["content"]
                logger.info("LLM response received successfully")
                return _parse_llm_response(message, section)
        except httpx.HTTPStatusError as exc:
            logger.error("LLM API returned error status %s: %s", exc.response.status_code, exc.response.text)
            return self._fallback_engine.evaluate(contract_text=contract_text, section=section, reason=f"API error: {exc.response.status_code}")
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("LLM call failed: %s", exc)
            return self._fallback_engine.evaluate(contract_text=contract_text, section=section, reason=str(exc))


def _build_prompt(*, contract_text: str, section: ChecklistSection) -> str:
    checklist_json = {
        "legal_requirements": section.legal_requirements,
        "company_requirements": section.company_requirements,
    }
    instructions = (
        "Review the contract text for each checklist item. Respond with JSON matching the schema:\n"
        "{\n  \"summary\": string,\n  \"items\": [\n    {\n      \"key\": string,\n      \"description\": string,\n      \"status\": \"✅\"|\"⚠️\"|\"❌\",\n      \"notes\": string,\n      \"category\": \"legal\"|\"company\"\n    }\n  ]\n}\n"
        "Use ✅ when requirement is clearly satisfied, ⚠️ when partially addressed, and ❌ when missing or contradictory."
    )
    return (
        f"Jurisdiction: {section.jurisdiction}\n"
        f"Contract type: {section.contract_type}\n"
        f"Checklist items: {json.dumps(checklist_json, ensure_ascii=False)}\n"
        f"Contract text:\n{contract_text[:15000]}\n"
        f"{instructions}"
    )


def _parse_llm_response(message: str, section: ChecklistSection) -> ChecklistEvaluation:
    parsed = _safe_json_loads(message)
    items_payload = parsed.get("items", [])
    items: list[ChecklistEvaluationItem] = []
    for item in items_payload:
        try:
            items.append(
                ChecklistEvaluationItem(
                    key=item["key"],
                    description=item.get("description") or _lookup_description(item["key"], section),
                    status=item.get("status", "⚠️"),
                    notes=item.get("notes", ""),
                    category=item.get("category", "legal"),
                )
            )
        except Exception as exc:  # pylint: disable=broad-except
            logger.debug("Skipping invalid LLM item: %s (%s)", item, exc)

    if not items:
        raise ValueError("LLM response did not include any evaluation items.")

    return ChecklistEvaluation(summary=parsed.get("summary", "Review completed."), items=items)


def _lookup_description(key: str, section: ChecklistSection) -> str:
    return (
        section.legal_requirements.get(key)
        or section.company_requirements.get(key)
        or "Description provided by LLM"
    )


def _safe_json_loads(message: str) -> Dict[str, object]:
    cleaned = message.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
    return json.loads(cleaned)


@dataclass
class HeuristicFallbackEngine:
    positive_keywords: Dict[str, Iterable[str]] | None = None

    def __post_init__(self) -> None:  # type: ignore[override]
        if self.positive_keywords is None:
            self.positive_keywords = {
                "rent_review_clause": ["rent review", "cpi", "market rent"],
                "termination_clause": ["terminate", "termination", "breach"],
                "assignment_terms": ["assign", "assignment", "sublet"],
                "force_majeure": ["force majeure", "act of god"],
                "notice": ["notice", "days' notice"],
            }

    def evaluate(self, *, contract_text: str, section: ChecklistSection, reason: str) -> ChecklistEvaluation:
        items: list[ChecklistEvaluationItem] = []
        lowered = contract_text.lower()

        def build_items(requirements: Dict[str, str | None], category: str) -> None:
            for key, description in requirements.items():
                status = self._guess_status(key, lowered)
                notes = "Heuristic evaluation" if status == "✅" else f"Fallback ({reason})"
                items.append(
                    ChecklistEvaluationItem(
                        key=key,
                        description=description or key.replace("_", " ").title(),
                        status=status,
                        notes=notes,
                        category=category,
                    )
                )

        build_items(section.legal_requirements, "legal")
        build_items(section.company_requirements, "company")

        summary = (
            "Heuristic-only review because the LLM could not be reached. "
            "Statuses are estimates—rerun once API access is configured."
        )
        return ChecklistEvaluation(summary=summary, items=items)

    def _guess_status(self, key: str, contract_text: str) -> str:
        keywords = (self.positive_keywords or {}).get(key, [])
        if any(keyword in contract_text for keyword in keywords):
            return "✅"
        return "⚠️"
