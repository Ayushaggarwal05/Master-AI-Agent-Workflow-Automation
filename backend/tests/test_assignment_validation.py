import pytest
from fastapi.testclient import TestClient
from backend.app.workflow.registry import get_workflow_registry
from backend.app.workflow.engine import WorkflowEngine
from backend.app.services.orchestrator import AgentOrchestrator
from backend.app.services.router import AIRouter
from backend.app.tools.calc_tools import CalculatorTool
from backend.app.tools.product_tools import DuplicateProductDetectorTool
from backend.app.tools.employee_tools import EmployeeRankingTool
from backend.app.tools.reporting_tools import ReportingTool
from backend.app.workflow.conditions import ConditionEvaluator

# ==============================================================================
# 1. PARAPHRASED & NATURAL LANGUAGE ROUTING VALIDATION (ALL 10 WORKFLOWS)
# ==============================================================================

@pytest.mark.parametrize("query,expected_wf", [
    ("Tell me what inventory I should reorder.", "WF001"),
    ("Which products are running low on stock?", "WF001"),
    ("Compare our product prices with the supplier list.", "WF002"),
    ("Check whether our vendor prices are significantly different from our internal prices.", "WF002"),
    ("Clean this supplier file.", "WF003"),
    ("Clean this vendor spreadsheet and identify invalid rows.", "WF003"),
    ("Generate product copy.", "WF004"),
    ("Write an SEO-friendly description for this product.", "WF004"),
    ("Track my order.", "WF005"),
    ("Where is order ORD-9021 right now?", "WF005"),
    ("Find products that look duplicated.", "WF006"),
    ("Find duplicate products in this catalog.", "WF006"),
    ("Plan a campaign.", "WF007"),
    ("Create a marketing campaign brief for our summer promotion.", "WF007"),
    ("Categorize these keywords.", "WF008"),
    ("Classify these SEO keywords by search intent.", "WF008"),
    ("Who is best suited for this task?", "WF009"),
    ("Which employee should handle this task?", "WF009"),
    ("Analyze workflow failures.", "WF010"),
    ("Show me how our workflows are performing.", "WF010"),
])
def test_paraphrased_semantic_routing(query: str, expected_wf: str):
    """Verifies that the AI Router correctly maps paraphrased natural language queries to workflows."""
    registry = get_workflow_registry()
    router = AIRouter(registry)
    selection = router.route(query)
    assert selection.workflow_id == expected_wf
    assert selection.confidence >= 0.80
    assert selection.reasoning != ""

# ==============================================================================
# 2. AMBIGUOUS REQUEST VALIDATION
# ==============================================================================

@pytest.mark.parametrize("ambiguous_query", [
    "Check my products.",
    "Analyze this product file.",
    "Review product information.",
    "Help me with inventory.",
])
def test_ambiguous_requests_require_clarification(test_client: TestClient, ambiguous_query: str):
    """Verifies that ambiguous queries returning low confidence are flagged as requiring clarification."""
    res = test_client.post("/execute", json={"message": ambiguous_query})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert data["error"] is not None
    assert data["error"]["code"] in ("AMBIGUOUS_REQUEST", "ROUTING_FAILED")
    assert "clarify" in data["error"]["message"].lower() or "multiple" in data["error"]["message"].lower()

# ==============================================================================
# 3. MISSING INPUTS VALIDATION
# ==============================================================================

def test_wf007_missing_campaign_goal_and_dates(test_client: TestClient):
    """WF007 without campaign goal or dates must prompt for missing inputs."""
    res = test_client.post("/execute", json={
        "message": "Create a marketing campaign brief for our summer promotion.",
        "inputs": {}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "MISSING_INPUT"
    missing = data["error"]["details"]["missing_inputs"]
    assert any("Campaign goal" in m or "goal" in m.lower() for m in missing)
    assert any("Dates" in m or "dates" in m.lower() for m in missing)

def test_wf005_missing_order_identifier(test_client: TestClient):
    """WF005 without order identifier must prompt for missing order ID or email."""
    res = test_client.post("/execute", json={
        "message": "Track my order and show delivery status.",
        "inputs": {}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "MISSING_INPUT"
    missing = data["error"]["details"]["missing_inputs"]
    assert any("order" in m.lower() or "email" in m.lower() for m in missing)

def test_wf004_missing_product_attributes_noted_in_output(test_client: TestClient):
    """WF004: When executed with incomplete product attributes, model does NOT hallucinate and flags missing fields."""
    res = test_client.post("/execute", json={
        "message": "Write an SEO-friendly description for this product.",
        "inputs": {
            "product_name": "Pro Wireless Headset",
            "category": "Audio"
            # material and color intentionally omitted
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    content = data["result"]["artifacts"]["generated_content"]
    assert "material" in content["explicitly_missing_attributes"]
    assert "color" in content["explicitly_missing_attributes"]

# ==============================================================================
# 4. DETERMINISTIC BUSINESS CONDITIONS & LOGIC VALIDATION
# ==============================================================================

def test_condition_wf001_restock_threshold():
    """Condition: current_stock < minimum_stock -> restock required."""
    calc = CalculatorTool()
    items = [
        {"sku": "SKU-A", "product_name": "Item A", "current_stock": 5, "minimum_stock": 10},
        {"sku": "SKU-B", "product_name": "Item B", "current_stock": 25, "minimum_stock": 10},
    ]
    res = calc.run(operation="stock_check", items=items, minimum_stock=10)
    assert res.success is True
    assert res.data["restock_required_count"] == 1
    assert res.data["restock_items"][0]["sku"] == "SKU-A"
    assert res.data["restock_items"][0]["suggested_reorder_qty"] == 15.0

def test_condition_wf002_price_difference_threshold():
    """Condition: price_difference > 10% -> exception flagged."""
    calc = CalculatorTool()
    products = [
        {"sku": "SKU-MATCH", "product_name": "Matched Item", "price": 100.0},
        {"sku": "SKU-DISCREPANCY", "product_name": "Discrepancy Item", "price": 100.0},
    ]
    vendor_prices = {
        "SKU-MATCH": 105.0,        # +5% (within 10% threshold)
        "SKU-DISCREPANCY": 130.0,  # +30% (>10% exception threshold)
    }
    res = calc.run(operation="price_comparison", products=products, vendor_prices=vendor_prices, threshold_pct=10.0)
    assert res.success is True
    assert res.data["total_matched"] == 2
    assert res.data["exception_count"] == 1
    assert res.data["exceptions"][0]["sku"] == "SKU-DISCREPANCY"
    assert res.data["exceptions"][0]["difference_pct"] == 30.0

def test_condition_wf006_exact_and_fuzzy_duplicates():
    """Condition: Exact SKU match = Definite Duplicate (100%), High attribute similarity = Possible Duplicate."""
    detector = DuplicateProductDetectorTool()
    products = [
        {"sku": "SKU-001", "name": "Logitech MX Master 3S Mouse", "category": "Peripherals", "price": 99.99},
        {"sku": "SKU-001", "name": "Logitech MX Master 3S Mouse Black", "category": "Peripherals", "price": 99.99}, # Exact SKU match
        {"sku": "SKU-002", "name": "Logitech MX Master 3S Ergonomic Mouse", "category": "Peripherals", "price": 99.99}, # Similar name/attributes
        {"sku": "SKU-003", "name": "Samsung 4K Curved Monitor 32-inch", "category": "Displays", "price": 399.99}, # Unrelated
    ]
    res = detector.run(products=products)
    assert res.success is True
    assert res.data["duplicates_found_count"] >= 1
    exact_matches = [d for d in res.data["duplicate_groups"] if "Exact SKU" in d["match_type"]]
    assert len(exact_matches) >= 1
    assert exact_matches[0]["confidence"] == 1.0

def test_condition_wf009_ranking_and_escalation():
    """Condition: Matching skills + available capacity -> assigned. No suitable candidates -> ESCALATION_REQUIRED."""
    ranking = EmployeeRankingTool()
    
    # Standard task with matching skillset
    res_assigned = ranking.run(
        task_description="Build asynchronous Python FastAPI REST backend with PostgreSQL ETL",
        required_skills=["Python", "FastAPI", "SQL"],
        priority="High"
    )
    assert res_assigned.success is True
    assert res_assigned.data["status"] == "ASSIGNED"
    assert res_assigned.data["recommended_employee"]["score"] > 25.0

    # Rare/impossible skill requirement triggers escalation condition
    res_escalated = ranking.run(
        task_description="Quantum Computing Hardware Firmware Assembly in Assembly8086",
        required_skills=["Quantum-FPGA-9000", "Assembly8086-Microcode"],
        priority="Urgent"
    )
    assert res_escalated.success is True
    assert res_escalated.data["status"] == "ESCALATION_REQUIRED"
    assert "No candidate" in res_escalated.data["reasoning"]

def test_condition_wf010_failure_rate_sla_flag():
    """Condition: failure_rate > 10% or avg_duration > 3.0s triggers workflow performance flag."""
    reporting = ReportingTool()
    logs = [
        {"workflow_id": "WF_BAD", "status": "FAILED", "duration_seconds": 4.5, "error_message": "Connection Timeout"},
        {"workflow_id": "WF_BAD", "status": "FAILED", "duration_seconds": 5.0, "error_message": "Connection Timeout"},
        {"workflow_id": "WF_BAD", "status": "SUCCESS", "duration_seconds": 3.8},
        {"workflow_id": "WF_GOOD", "status": "SUCCESS", "duration_seconds": 0.8},
        {"workflow_id": "WF_GOOD", "status": "SUCCESS", "duration_seconds": 0.9},
    ]
    res = reporting.run(logs=logs, fail_threshold_pct=10.0, time_threshold_sec=3.0)
    assert res.success is True
    flagged = res.data["flagged_workflows"]
    assert len(flagged) == 1
    assert flagged[0]["workflow_id"] == "WF_BAD"
    assert flagged[0]["failure_rate_pct"] == 66.67
    assert len(res.data["recommendations"]) >= 1

# ==============================================================================
# 5. ERROR HANDLING & TRACE VERIFICATION
# ==============================================================================

def test_nonexistent_order_handled_gracefully(test_client: TestClient):
    """WF005: Nonexistent order ID returns structured error without server crash."""
    res = test_client.post("/execute", json={
        "message": "Where is order ORD-NONEXISTENT-9999?",
        "inputs": {"order_id": "ORD-NONEXISTENT-9999"}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert data["execution"]["status"] == "failed"
    assert "ORD-NONEXISTENT-9999" in data["error"]["message"]
    # Check trace includes error event
    trace_events = [e["type"] for e in data["execution"]["trace"]]
    assert "error" in trace_events

def test_missing_file_handled_gracefully(test_client: TestClient):
    """WF003 with invalid file path returns structured error without crashing."""
    res = test_client.post("/execute", json={
        "message": "Clean this vendor spreadsheet and identify invalid rows.",
        "inputs": {"file_path": "non_existent_file_12345.csv"}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert "file" in data["error"]["message"].lower() or "not found" in data["error"]["message"].lower()
