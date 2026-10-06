import pytest
from backend.app.workflow.models import WorkflowDefinition
from backend.app.workflow.registry import get_workflow_registry
from backend.app.workflow.engine import WorkflowEngine
from backend.app.tools.registry import get_tool_registry, FunctionTool
from backend.app.tools.base import ToolResult

def test_add_wf011_without_modifying_core_engine():
    """
    Demonstrates architectural scalability:
    Registers a new hypothetical workflow 'WF011' and a custom tool,
    then executes it through the generic WorkflowEngine with zero modifications to engine code.
    """
    # 1. Register a custom domain tool in ToolRegistry
    tool_registry = get_tool_registry()
    
    def currency_converter(amount: float = 100.0, rate: float = 1.08, **kwargs):
        converted = round(amount * rate, 2)
        return ToolResult(success=True, data={"original": amount, "converted_eur": converted})

    tool_registry.register(FunctionTool(
        name="currency_converter",
        description="Converts USD amount to EUR",
        func=currency_converter
    ))
    assert tool_registry.exists("currency_converter")

    # 2. Define hypothetical WF011
    wf011 = WorkflowDefinition(
        id="WF011",
        name="Multi-Currency Revenue Conversion",
        trigger="User asks to convert sales figures to foreign currency.",
        inputs=["Sales revenue USD", "Exchange rate"],
        steps=[
            "Load USD sales figures",
            "Calculate EUR converted revenue",
            "Generate financial summary"
        ],
        decision="Apply standard market spot rate.",
        tools=["currency_converter"],
        output="Converted financial report in EUR."
    )

    # 3. Register WF011 dynamically into WorkflowRegistry
    registry = get_workflow_registry()
    registry.register(wf011)
    assert registry.exists("WF011")
    assert registry.get("WF011").name == "Multi-Currency Revenue Conversion"

    # 4. Execute WF011 using the EXACT same generic WorkflowEngine
    engine = WorkflowEngine(tool_registry=tool_registry)
    result = engine.execute(
        workflow=wf011,
        input_data={"amount": 2500.0, "rate": 1.10}
    )

    assert result.success is True
    assert result.workflow_id == "WF011"
    assert len(result.trace) > 0
    assert result.output_summary == "Converted financial report in EUR."
