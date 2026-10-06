import pytest
from backend.app.services.router import AIRouter
from backend.app.workflow.registry import get_workflow_registry

@pytest.fixture
def router():
    registry = get_workflow_registry()
    return AIRouter(registry)

def test_route_restock_request_to_wf001(router: AIRouter):
    """User asks which products need restocking -> WF001."""
    selection = router.route("Which products are running low on stock and need restocking?")
    assert selection.workflow_id == "WF001"
    assert selection.confidence >= 0.80
    assert len(selection.required_inputs) > 0
    assert "stock" in selection.reasoning.lower() or "inventory" in selection.reasoning.lower()

def test_route_price_validation_to_wf002(router: AIRouter):
    """User asks to validate product prices against vendor list -> WF002."""
    selection = router.route("Check whether our vendor prices differ significantly from our internal prices.")
    assert selection.workflow_id == "WF002"
    assert selection.confidence >= 0.80

def test_route_vendor_file_to_wf003(router: AIRouter):
    """User provides vendor data file -> WF003."""
    selection = router.route("Please clean and validate this new vendor product data file.")
    assert selection.workflow_id == "WF003"
    assert selection.confidence >= 0.80

def test_route_description_generator_to_wf004(router: AIRouter):
    """User asks to generate product content -> WF004."""
    selection = router.route("Generate eCommerce product descriptions and SEO metadata for our new keyboard.")
    assert selection.workflow_id == "WF004"
    assert selection.confidence >= 0.80

def test_route_order_status_to_wf005(router: AIRouter):
    """User asks for order status -> WF005."""
    selection = router.route("Where is my order ORD-9021? Can you check the shipment tracking status?")
    assert selection.workflow_id == "WF005"
    assert selection.confidence >= 0.80

def test_route_duplicate_detection_to_wf006(router: AIRouter):
    """User asks to find duplicates in product catalog -> WF006."""
    selection = router.route("Scan our catalog to find duplicate products and matching SKUs.")
    assert selection.workflow_id == "WF006"
    assert selection.confidence >= 0.80

def test_route_campaign_brief_to_wf007(router: AIRouter):
    """User asks to create campaign brief -> WF007."""
    selection = router.route("Create a marketing campaign brief for the upcoming Spring sale promotion.")
    assert selection.workflow_id == "WF007"
    assert selection.confidence >= 0.80

def test_route_keyword_classification_to_wf008(router: AIRouter):
    """User uploads keywords for SEO intent classification -> WF008."""
    selection = router.route("Classify these SEO search keywords by search intent and category priority.")
    assert selection.workflow_id == "WF008"
    assert selection.confidence >= 0.80

def test_route_employee_assignment_to_wf009(router: AIRouter):
    """Manager asks to assign task -> WF009."""
    selection = router.route("Who is the best employee to assign this Python FastAPI backend development task to?")
    assert selection.workflow_id == "WF009"
    assert selection.confidence >= 0.80

def test_route_performance_report_to_wf010(router: AIRouter):
    """User asks for workflow execution performance report -> WF010."""
    selection = router.route("Generate a workflow performance report showing failure rates and execution bottlenecks.")
    assert selection.workflow_id == "WF010"
    assert selection.confidence >= 0.80

def test_route_unknown_request_handled_safely(router: AIRouter):
    """Unknown or unrelated user request returns UNKNOWN without crashing."""
    selection = router.route("What is the recipe for chocolate chip cookies?")
    assert selection.workflow_id == "UNKNOWN"
    assert selection.confidence < 0.50

def test_adaptive_vector_routing_strategy_when_catalog_exceeds_threshold():
    """Verifies that when catalog size exceeds threshold (e.g. 35 workflows), router filters via vector search."""
    from backend.app.workflow.models import WorkflowDefinition
    from backend.app.workflow.registry import WorkflowRegistry
    from backend.app.workflow.trace import ExecutionTrace

    custom_registry = WorkflowRegistry()
    # Register 35 mock workflows
    for i in range(1, 36):
        wf_id = f"WF{i:03d}"
        custom_registry.register(WorkflowDefinition(
            id=wf_id,
            name=f"Workflow Test {i}",
            trigger=f"Automated test trigger for workflow {i}",
            inputs=["test_input"],
            steps=["Step 1"],
            decision=f"Run if step {i} valid",
            tools=["csv_reader"],
            output=f"Output {i}"
        ))

    router = AIRouter(custom_registry)
    trace = ExecutionTrace()
    selection = router.route("Automated test trigger for workflow 15", trace=trace)
    
    events = [e.type for e in trace.events]
    assert "vector_recall" in events
    assert "routing_strategy_selected" in events
    strategy_event = next(e for e in trace.events if e.type == "routing_strategy_selected")
    assert "vector_recall_top_" in strategy_event.details["strategy"]
    assert strategy_event.details["total_workflows"] == 35


