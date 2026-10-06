from pathlib import Path
import pytest
from backend.app.workflow.registry import WorkflowRegistry, WorkflowNotFoundError
from backend.app.workflow.models import WorkflowDefinition

def test_registry_operations(excel_path: Path):
    """Test registry indexing, retrieval, existence checks and metadata."""
    registry = WorkflowRegistry()
    count = registry.load_from_excel(excel_path)
    assert count == 10
    assert registry.count() == 10
    
    # Check exists
    assert registry.exists("WF001")
    assert registry.exists("wf001") # Case-insensitivity
    assert registry.exists("WF010")
    assert not registry.exists("WF999")
    
    # Check get
    wf1 = registry.get("WF001")
    assert wf1 is not None
    assert wf1.name == "Inventory Restock Check"
    
    # Check get_or_raise
    wf_raised = registry.get_or_raise("WF002")
    assert wf_raised.name == "Product Price Validation"
    
    with pytest.raises(WorkflowNotFoundError):
        registry.get_or_raise("WF_INVALID")

    # Check list_all
    all_wfs = registry.list_all()
    assert len(all_wfs) == 10
    assert all_wfs[0].id == "WF001"
    assert all_wfs[-1].id == "WF010"

    # Check router metadata format
    router_meta = registry.get_metadata_for_router()
    assert len(router_meta) == 10
    first_meta = router_meta[0]
    assert "id" in first_meta
    assert "trigger" in first_meta
    assert "tools" in first_meta
    assert "step_count" in first_meta
