# Test Suite Documentation

## Overview

This test suite provides comprehensive coverage for the Contract Review Agent application, including unit tests for core components and integration tests for API endpoints and service workflows.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── fixtures/
│   ├── __init__.py
│   └── sample_contract.txt   # Sample contract for testing
├── test_ingestion.py        # Unit tests for document ingestion
├── test_checklist_loader.py # Unit tests for checklist loading
├── test_llm_agent.py        # Unit tests for LLM agent (with mocking)
├── test_report_generator.py # Unit tests for report generation
├── test_api.py              # Integration tests for API endpoints
└── test_review_service.py  # Integration tests for review service
```

## Running Tests

### Install Dependencies

First, ensure you have the testing dependencies installed:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=app --cov-report=html
```

View the HTML coverage report by opening `htmlcov/index.html` in your browser.

### Run Specific Test Files

```bash
pytest tests/test_ingestion.py
pytest tests/test_api.py
```

### Run by Marker

```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
```

### Run with Verbose Output

```bash
pytest -v
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)

- **test_ingestion.py**: Tests document text extraction from PDF, DOCX, and TXT files
- **test_checklist_loader.py**: Tests checklist JSON loading and section retrieval
- **test_llm_agent.py**: Tests LLM agent with mocked API calls and heuristic fallback
- **test_report_generator.py**: Tests markdown report generation and formatting

### Integration Tests (`@pytest.mark.integration`)

- **test_api.py**: Tests FastAPI endpoints (health check, index page, contract review)
- **test_review_service.py**: Tests end-to-end review workflow

## Test Fixtures

Key fixtures available in `conftest.py`:

- `sample_checklist_data`: Sample checklist JSON data
- `temp_checklist_file`: Temporary checklist JSON file
- `sample_checklist_section`: ChecklistSection model instance
- `sample_evaluation`: ChecklistEvaluation model instance
- `sample_contract_text`: Path to sample contract file
- `temp_dir`: Temporary directory for test files
- `mock_env_vars`: Mocked environment variables

## Mocking Strategy

- **LLM API calls**: Mocked using `unittest.mock.patch` to avoid actual API calls
- **Telegram API**: Mocked to return `TelegramDispatchResult` without sending messages
- **Google Drive**: Uses placeholder implementation (no actual uploads)
- **External services**: All external dependencies are mocked to ensure tests run independently

## Notes

- Tests are designed to run without requiring actual API keys or credentials
- The heuristic fallback engine is used when API keys are not provided
- All file operations use temporary directories that are cleaned up automatically
- Integration tests may require the main checklist file (`contract_checklist.json`) to exist

