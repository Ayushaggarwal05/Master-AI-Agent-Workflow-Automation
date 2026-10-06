import pytest
from backend.app.workflow.engine import WorkflowEngine
from backend.app.workflow.trace import ExecutionTrace
from backend.app.workflow.registry import get_workflow_registry

def test_engine_executes_workflow_and_captures_trace():
    registry = get_workflow_registry()
    wf = registry.get_or_raise("WF001")
    
    engine = WorkflowEngine()
    trace = ExecutionTrace()
    
    result = engine.execute(
        workflow=wf,
        input_data={"minimum_stock_threshold": 10},
        trace=trace
    )
    
    assert result.success is True
    assert result.workflow_id == "WF001"
    assert "restock_report" in result.data["artifacts"]
    assert result.total_duration_ms > 0
    
    # Verify trace structure
    events = [e["type"] for e in result.trace]
    assert "input_validation" in events
    assert "step_started" in events
    assert "tool_called" in events
    assert "tool_result" in events
    assert "condition_evaluated" in events
    assert "step_completed" in events
    assert "final_result" in events

def test_engine_handles_unknown_tool_gracefully():
    # Construct synthetic workflow with non-existent tool
    from backend.app.workflow.models import WorkflowDefinition
    bad_wf = WorkflowDefinition(
        id="WF_BAD",
        name="Bad Tool Workflow",
        trigger="Test trigger",
        inputs=["None"],
        steps=["Execute mythical step"],
        decision="None",
        tools=["non_existent_tool_xyz"],
        output="Result"
    )
    engine = WorkflowEngine()
    res = engine.execute(workflow=bad_wf, input_data={})
    # Should complete with generic executor or handle cleanly
    assert isinstance(res.trace, list)
