import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.workflow.registry import get_workflow_registry
from backend.app.workflow.loader import ExcelWorkflowLoader

@pytest.fixture(scope="session")
def excel_path() -> Path:
    """Returns the path to the real workflows.xlsx dataset."""
    path = settings.resolved_excel_path
    assert path.exists(), f"Excel file does not exist at {path}"
    return path

@pytest.fixture(scope="session", autouse=True)
def init_registry(excel_path):
    """Initializes the workflow registry before tests run."""
    registry = get_workflow_registry()
    registry.load_from_excel(excel_path)
    return registry

@pytest.fixture
def test_client() -> TestClient:
    """Provides a FastAPI TestClient instance."""
    with TestClient(app) as client:
        yield client

@pytest.fixture(autouse=True)
def mock_llm_for_test_suite(monkeypatch):
    """Ensures test suite runs with deterministic SemanticEngineProvider to prevent API quota exhaustion."""
    from backend.app.core.llm import SemanticEngineProvider
    fallback = SemanticEngineProvider()
    monkeypatch.setattr("backend.app.core.llm.get_llm_provider", lambda: fallback)
    monkeypatch.setattr("backend.app.services.router.get_llm_provider", lambda: fallback)
    monkeypatch.setattr("backend.app.tools.llm_tools.get_llm_provider", lambda: fallback)


