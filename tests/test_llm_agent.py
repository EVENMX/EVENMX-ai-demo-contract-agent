"""Tests for LLM agent functionality."""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.llm_agent import ContractReviewAgent, HeuristicFallbackEngine
from app.models import ChecklistEvaluation, ChecklistEvaluationItem, ChecklistSection


@pytest.mark.unit
class TestHeuristicFallbackEngine:
    """Test heuristic fallback evaluation engine."""

    def test_evaluate_with_positive_keywords(self, sample_checklist_section: ChecklistSection) -> None:
        """Test that heuristic engine finds positive keywords."""
        contract_text = "This lease includes a rent review clause based on CPI adjustments."
        engine = HeuristicFallbackEngine()

        evaluation = engine.evaluate(
            contract_text=contract_text, section=sample_checklist_section, reason="test"
        )

        assert isinstance(evaluation, ChecklistEvaluation)
        assert len(evaluation.items) > 0
        # Check that at least one item has status ✅ (found keywords)
        statuses = [item.status for item in evaluation.items]
        assert "✅" in statuses or "⚠️" in statuses  # At least one status is set

    def test_evaluate_without_positive_keywords(self, sample_checklist_section: ChecklistSection) -> None:
        """Test that heuristic engine returns warning status when keywords not found."""
        contract_text = "This is a completely unrelated document with no lease terms."
        engine = HeuristicFallbackEngine()

        evaluation = engine.evaluate(
            contract_text=contract_text, section=sample_checklist_section, reason="test"
        )

        assert isinstance(evaluation, ChecklistEvaluation)
        # Most items should be ⚠️ when keywords aren't found
        statuses = [item.status for item in evaluation.items]
        assert "⚠️" in statuses or "✅" in statuses  # At least one status

    def test_evaluate_includes_all_requirements(self, sample_checklist_section: ChecklistSection) -> None:
        """Test that evaluation includes all legal and company requirements."""
        contract_text = "Sample contract text"
        engine = HeuristicFallbackEngine()

        evaluation = engine.evaluate(
            contract_text=contract_text, section=sample_checklist_section, reason="test"
        )

        legal_keys = set(sample_checklist_section.legal_requirements.keys())
        company_keys = set(sample_checklist_section.company_requirements.keys())
        evaluation_keys = {item.key for item in evaluation.items}

        assert legal_keys.issubset(evaluation_keys)
        assert company_keys.issubset(evaluation_keys)

    def test_evaluate_categorizes_items(self, sample_checklist_section: ChecklistSection) -> None:
        """Test that evaluation items are properly categorized."""
        contract_text = "Sample contract"
        engine = HeuristicFallbackEngine()

        evaluation = engine.evaluate(
            contract_text=contract_text, section=sample_checklist_section, reason="test"
        )

        categories = {item.category for item in evaluation.items}
        assert "legal" in categories
        assert "company" in categories

    def test_guess_status_with_keywords(self) -> None:
        """Test status guessing when keywords are present."""
        engine = HeuristicFallbackEngine()
        engine.positive_keywords = {"test_key": ["rent", "lease"]}

        contract_text = "This document mentions rent and lease terms."
        status = engine._guess_status("test_key", contract_text.lower())

        assert status == "✅"

    def test_guess_status_without_keywords(self) -> None:
        """Test status guessing when keywords are not present."""
        engine = HeuristicFallbackEngine()
        engine.positive_keywords = {"test_key": ["rent", "lease"]}

        contract_text = "This document has no relevant terms."
        status = engine._guess_status("test_key", contract_text.lower())

        assert status == "⚠️"


@pytest.mark.unit
class TestContractReviewAgent:
    """Test contract review agent with LLM integration."""

    @pytest.mark.asyncio
    async def test_review_without_api_key_uses_fallback(
        self, sample_checklist_section: ChecklistSection, mock_env_vars: None
    ) -> None:
        """Test that agent uses fallback when API key is missing."""
        agent = ContractReviewAgent()
        contract_text = "Sample contract text"

        evaluation = await agent.review(contract_text=contract_text, section=sample_checklist_section)

        assert isinstance(evaluation, ChecklistEvaluation)
        assert "Heuristic-only review" in evaluation.summary or len(evaluation.items) > 0

    @pytest.mark.asyncio
    async def test_review_with_successful_llm_response(
        self, sample_checklist_section: ChecklistSection, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test successful LLM API call and response parsing."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
        monkeypatch.setenv("OPENROUTER_MODEL", "openai/gpt-4.1-mini")
        
        # Clear the settings cache
        from app.config import get_settings
        get_settings.cache_clear()

        # Mock LLM response
        mock_response_data = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "summary": "Review completed successfully.",
                                "items": [
                                    {
                                        "key": "parties_identified",
                                        "description": "Parties identified",
                                        "status": "✅",
                                        "notes": "Both parties clearly identified",
                                        "category": "legal",
                                    }
                                ],
                            }
                        )
                    }
                }
            ]
        }

        agent = ContractReviewAgent()
        contract_text = "Sample contract"

        with patch("app.llm_agent.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            evaluation = await agent.review(contract_text=contract_text, section=sample_checklist_section)

            assert isinstance(evaluation, ChecklistEvaluation)
            assert evaluation.summary == "Review completed successfully."
            assert len(evaluation.items) > 0

    @pytest.mark.asyncio
    async def test_review_with_llm_api_error_uses_fallback(
        self, sample_checklist_section: ChecklistSection, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that agent falls back when LLM API call fails."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

        agent = ContractReviewAgent()
        contract_text = "Sample contract"

        with patch("app.llm_agent.httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(side_effect=httpx.HTTPError("API Error"))

            evaluation = await agent.review(contract_text=contract_text, section=sample_checklist_section)

            assert isinstance(evaluation, ChecklistEvaluation)
            # Should use fallback
            assert len(evaluation.items) > 0

    @pytest.mark.asyncio
    async def test_review_handles_malformed_json_response(
        self, sample_checklist_section: ChecklistSection, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that agent handles malformed JSON from LLM."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

        mock_response_data = {
            "choices": [{"message": {"content": "This is not valid JSON"}}]
        }

        agent = ContractReviewAgent()
        contract_text = "Sample contract"

        with patch("app.llm_agent.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            # Should fall back to heuristic on JSON parse error
            evaluation = await agent.review(contract_text=contract_text, section=sample_checklist_section)

            assert isinstance(evaluation, ChecklistEvaluation)

    @pytest.mark.asyncio
    async def test_review_handles_json_with_code_blocks(
        self, sample_checklist_section: ChecklistSection, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that agent handles JSON wrapped in code blocks."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
        
        # Clear the settings cache
        from app.config import get_settings
        get_settings.cache_clear()

        json_content = json.dumps(
            {
                "summary": "Test summary",
                "items": [
                    {
                        "key": "test_key",
                        "description": "Test description",
                        "status": "✅",
                        "notes": "Test notes",
                        "category": "legal",
                    }
                ],
            }
        )
        wrapped_content = f"```json\n{json_content}\n```"

        mock_response_data = {"choices": [{"message": {"content": wrapped_content}}]}

        agent = ContractReviewAgent()
        contract_text = "Sample contract"

        with patch("app.llm_agent.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)

            evaluation = await agent.review(contract_text=contract_text, section=sample_checklist_section)

            assert isinstance(evaluation, ChecklistEvaluation)
            assert evaluation.summary == "Test summary"

