import pytest
from backend.app.workflow.models import WorkflowDefinition
from backend.app.workflow.validator import WorkflowValidator, WorkflowValidationError

def test_validator_detects_duplicate_workflow_ids():
    """Test 5: Duplicate workflow IDs are detected and rejected."""
    wf1 = WorkflowDefinition(
        id="WF001",
        name="Workflow 1",
        trigger="Trigger 1",
        inputs=["Input 1"],
        steps=["Step 1"],
        decision="Rule 1",
        tools=["Tool 1"],
        output="Output 1"
    )
    wf2 = WorkflowDefinition(
        id="WF001",  # Duplicate ID
        name="Workflow 2",
        trigger="Trigger 2",
        inputs=["Input 2"],
        steps=["Step 2"],
        decision="Rule 2",
        tools=["Tool 2"],
        output="Output 2"
    )
    
    with pytest.raises(WorkflowValidationError) as exc_info:
        WorkflowValidator.validate_workflow_collection([wf1, wf2])
    
    assert "Duplicate workflow IDs detected: WF001" in str(exc_info.value.errors)

def test_validator_rejects_missing_required_fields():
    """Test 6: Invalid workflow data is rejected (empty name, trigger, steps, tools, output)."""
    # Raw row missing id
    errors = WorkflowValidator.validate_raw_row({"name": "Test", "trigger": "T"}, row_number=2)
    assert any("Missing required field 'id'" in e for e in errors)
    
    # Raw row missing trigger
    errors = WorkflowValidator.validate_raw_row({"id": "WF001", "name": "Test"}, row_number=2)
    assert any("Missing required field 'trigger'" in e for e in errors)

    # Parsed definition with empty steps or tools
    wf_empty_steps = WorkflowDefinition(
        id="WF001",
        name="Name",
        trigger="Trigger",
        steps=[],
        decision="Dec",
        tools=["tool"],
        output="out"
    )
    errors = WorkflowValidator.validate_workflow_definition(wf_empty_steps)
    assert any("must contain at least one valid step" in e for e in errors)

    wf_empty_tools = WorkflowDefinition(
        id="WF001",
        name="Name",
        trigger="Trigger",
        steps=["Step 1"],
        decision="Dec",
        tools=[],
        output="out"
    )
    errors = WorkflowValidator.validate_workflow_definition(wf_empty_tools)
    assert any("must specify at least one tool" in e for e in errors)

def test_validator_rejects_empty_collection():
    """Test empty collection validation."""
    with pytest.raises(WorkflowValidationError):
        WorkflowValidator.validate_workflow_collection([])
