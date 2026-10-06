import pytest
from fastapi.testclient import TestClient

def test_health_endpoint(test_client: TestClient):
    """Test 7: GET /health works and returns status, version, and workflow count."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["workflows_loaded"] == 10
    assert "version" in data
    assert "excel_path" in data

def test_get_all_workflows(test_client: TestClient):
    """Test 8: GET /workflows returns all 10 workflow definitions."""
    response = test_client.get("/workflows")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert data["total"] == 10
    assert len(data["workflows"]) == 10
    
    # Verify expected workflow IDs exist in response
    ids = [w["id"] for w in data["workflows"]]
    assert "WF001" in ids
    assert "WF010" in ids

def test_get_workflow_by_id_wf001(test_client: TestClient):
    """Test 9: GET /workflows/WF001 returns exact workflow details."""
    response = test_client.get("/workflows/WF001")
    assert response.status_code == 200
    data = response.json()
    assert "workflow" in data
    wf = data["workflow"]
    assert wf["id"] == "WF001"
    assert wf["name"] == "Inventory Restock Check"
    assert isinstance(wf["inputs"], list)
    assert isinstance(wf["steps"], list)
    assert isinstance(wf["tools"], list)
    assert "CSV reader" in wf["tools"]
    assert wf["decision"] != ""
    assert wf["output"] != ""

def test_get_workflow_by_id_wf010(test_client: TestClient):
    """Test GET /workflows/WF010 returns exact details for WF010."""
    response = test_client.get("/workflows/WF010")
    assert response.status_code == 200
    wf = response.json()["workflow"]
    assert wf["id"] == "WF010"
    assert wf["name"] == "Workflow Performance Report"
    assert "reporting" in wf["tools"]

def test_get_workflow_unknown_id_returns_404(test_client: TestClient):
    """Test 10: Unknown workflow ID returns an appropriate 404."""
    response = test_client.get("/workflows/WF999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data or "message" in data

def test_api_v1_prefixed_routes(test_client: TestClient):
    """Test that routes are also accessible under /api/v1 prefix."""
    res_health = test_client.get("/api/v1/health")
    assert res_health.status_code == 200
    
    res_wf = test_client.get("/api/v1/workflows")
    assert res_wf.status_code == 200
    assert res_wf.json()["total"] == 10

def test_router_metadata_endpoint(test_client: TestClient):
    """Test GET /workflows/router-metadata for Stage 2 AI routing."""
    response = test_client.get("/workflows/router-metadata")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 10
    assert all("id" in item and "trigger" in item for item in items)

def test_file_upload_endpoint(test_client: TestClient):
    """Test POST /upload accepts valid CSV file and returns path."""
    csv_content = b"sku,current_stock,minimum_stock\nPROD-001,5,10\n"
    response = test_client.post(
        "/upload",
        files={"file": ("test_inventory.csv", csv_content, "text/csv")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "test_inventory.csv" in data["filename"]
    assert "file_path" in data

def test_invalid_file_upload_rejected(test_client: TestClient):
    """Test POST /upload rejects unauthorized file extensions (e.g. .exe)."""
    response = test_client.post(
        "/upload",
        files={"file": ("malicious.exe", b"binary content", "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

