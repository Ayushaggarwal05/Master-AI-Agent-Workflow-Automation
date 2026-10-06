import pytest
from fastapi.testclient import TestClient
from backend.app.services.orchestrator import AgentOrchestrator

def test_wf001_inventory_restock_execution(test_client: TestClient):
    """WF001: Inventory Restock Check."""
    res = test_client.post("/execute", json={
        "message": "Which products need restocking right now?",
        "inputs": {"minimum_stock_threshold": 10}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["workflow"]["id"] == "WF001"
    assert data["execution"]["status"] == "completed"
    assert "restock_report" in data["result"]["artifacts"]
    report = data["result"]["artifacts"]["restock_report"]
    assert report["restock_required_count"] >= 1

def test_wf002_price_validation_execution(test_client: TestClient):
    """WF002: Product Price Validation."""
    res = test_client.post("/execute", json={
        "message": "Validate our product prices against vendor price lists.",
        "inputs": {}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["workflow"]["id"] == "WF002"
    assert "price_validation_report" in data["result"]["artifacts"]
    report = data["result"]["artifacts"]["price_validation_report"]
    assert "matched_products" in report

def test_wf003_vendor_file_processing_execution(test_client: TestClient):
    """WF003: Vendor File Processing."""
    res = test_client.post("/execute", json={
        "message": "Process and validate this vendor product file.",
        "inputs": {"file_path": "sample_data/vendor_products.csv"}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["workflow"]["id"] == "WF003"
    assert "validation_summary" in data["result"]["artifacts"]
    val = data["result"]["artifacts"]["validation_summary"]
    assert val["valid_count"] > 0
    assert val["invalid_count"] > 0 # Rows missing SKU or Name

def test_wf004_product_description_execution(test_client: TestClient):
    """WF004: Product Description Generator."""
    res = test_client.post("/execute", json={
        "message": "Generate product descriptions and SEO metadata.",
        "inputs": {
            "product_name": "UltraLight Carbon Mouse",
            "category": "Peripherals",
            "attributes": "Weight: 49g, Optical Sensor 26k DPI",
            "material": "Carbon Fiber",
            "color": "Matte White",
            "target_audience": "Competitive Gamers"
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["workflow"]["id"] == "WF004"
    assert "generated_content" in data["result"]["artifacts"]
    content = data["result"]["artifacts"]["generated_content"]
    assert "seo_title" in content
    assert "meta_description" in content

def test_wf005_customer_order_status_execution(test_client: TestClient):
    """WF005: Customer Order Status."""
    res = test_client.post("/execute", json={
        "message": "Check status for order ORD-9021",
        "inputs": {"order_id": "ORD-9021"}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["workflow"]["id"] == "WF005"
    assert "order" in data["result"]["artifacts"]
    assert "shipment" in data["result"]["artifacts"]
    assert data["result"]["artifacts"]["order"]["order_id"] == "ORD-9021"

def test_wf006_duplicate_product_detection_execution(test_client: TestClient):
    """WF006: Duplicate Product Detection."""
    res = test_client.post("/execute", json={
        "message": "Find duplicate products in catalog",
        "inputs": {}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["workflow"]["id"] == "WF006"
    assert "duplicate_report" in data["result"]["artifacts"]

def test_wf007_campaign_brief_execution(test_client: TestClient):
    """WF007: Marketing Campaign Brief."""
    res = test_client.post("/execute", json={
        "message": "Create a marketing campaign brief for our spring promotion",
        "inputs": {
            "campaign_goal": "Boost Q2 revenue by 20%",
            "product_list": ["Ergonomic Wireless Mouse", "Mechanical Keyboard"],
            "dates": "April 15 - May 30, 2026",
            "promotion": "Bundle Discount 15% OFF"
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["workflow"]["id"] == "WF007"
    assert "campaign_brief" in data["result"]["artifacts"]
    brief = data["result"]["artifacts"]["campaign_brief"]
    assert "campaign_checklist" in brief

def test_wf008_seo_keyword_classification_execution(test_client: TestClient):
    """WF008: SEO Keyword Classification."""
    res = test_client.post("/execute", json={
        "message": "Classify these SEO keywords by intent and category",
        "inputs": {}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["workflow"]["id"] == "WF008"
    assert "keyword_classification_report" in data["result"]["artifacts"]

def test_wf009_employee_task_assignment_execution(test_client: TestClient):
    """WF009: Employee Task Assignment."""
    res = test_client.post("/execute", json={
        "message": "Assign employee to develop Python ETL data pipeline",
        "inputs": {
            "task_description": "Build asynchronous Python FastAPI backend ETL pipeline",
            "skills": ["Python", "FastAPI", "ETL", "SQL"],
            "priority": "High",
            "deadline": "Friday"
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["workflow"]["id"] == "WF009"
    assert "assignment_result" in data["result"]["artifacts"]
    assignment = data["result"]["artifacts"]["assignment_result"]
    assert assignment["status"] == "ASSIGNED"
    assert "recommended_employee" in assignment

def test_wf010_workflow_performance_report_execution(test_client: TestClient):
    """WF010: Workflow Performance Report."""
    res = test_client.post("/execute", json={
        "message": "Generate workflow performance report from execution logs",
        "inputs": {}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["workflow"]["id"] == "WF010"
    assert "performance_report" in data["result"]["artifacts"]
    report = data["result"]["artifacts"]["performance_report"]
    assert "summary_metrics" in report
    assert "flagged_workflows" in report
