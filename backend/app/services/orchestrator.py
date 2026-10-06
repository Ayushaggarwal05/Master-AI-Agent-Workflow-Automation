from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.app.core.logging import get_logger
from backend.app.workflow.models import WorkflowDefinition, WorkflowSummary
from backend.app.workflow.registry import WorkflowRegistry, get_workflow_registry
from backend.app.workflow.engine import WorkflowEngine, WorkflowExecutionResult
from backend.app.workflow.trace import ExecutionTrace
from backend.app.services.router import AIRouter, WorkflowSelection

logger = get_logger(__name__)

class ErrorDetails(BaseModel):
    """Structured error information."""
    code: str
    message: str
    failed_step: Optional[str] = None
    tool: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class ExecutionSummary(BaseModel):
    """Execution status and performance summary."""
    status: str
    total_duration_ms: float
    events_count: int
    trace: List[Dict[str, Any]]


class ExecuteResponse(BaseModel):
    """API response model for workflow execution."""
    success: bool
    workflow: Optional[WorkflowSummary] = None
    routing: WorkflowSelection
    execution: ExecutionSummary
    result: Optional[Dict[str, Any]] = None
    error: Optional[ErrorDetails] = None


class AgentOrchestrator:
    """
    Main orchestration service coordinating the AI Router, Workflow Registry,
    and Generic Workflow Execution Engine.
    """

    def __init__(
        self, 
        registry: Optional[WorkflowRegistry] = None,
        engine: Optional[WorkflowEngine] = None,
        router: Optional[AIRouter] = None
    ):
        self.registry = registry or get_workflow_registry()
        self.engine = engine or WorkflowEngine()
        self.router = router or AIRouter(self.registry)

    def run(
        self, 
        message: str, 
        inputs: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None
    ) -> ExecuteResponse:
        """
        Orchestrates full workflow execution from user intent to final result.
        """
        trace = ExecutionTrace()
        inputs = inputs or {}

        # 1. Routing phase
        if workflow_id:
            # Explicit workflow execution requested
            target_wf = self.registry.get(workflow_id)
            if not target_wf:
                err = ErrorDetails(
                    code="WORKFLOW_NOT_FOUND",
                    message=f"Workflow with ID '{workflow_id}' not found in registry."
                )
                return self._create_error_response(
                    routing=WorkflowSelection(
                        workflow_id=workflow_id,
                        confidence=1.0,
                        reasoning="Manual override by caller.",
                        required_inputs=[],
                        missing_inputs=[]
                    ),
                    error=err,
                    trace=trace
                )
            selection = WorkflowSelection(
                workflow_id=target_wf.id,
                confidence=1.0,
                reasoning="Manual workflow specification by client.",
                required_inputs=target_wf.inputs,
                missing_inputs=[]
            )
            trace.record(event_type="workflow_selected", details={"workflow_id": target_wf.id, "mode": "explicit"})
        else:
            selection = self.router.route(message=message, provided_inputs=inputs, trace=trace)

        if selection.workflow_id == "UNKNOWN" or selection.confidence < 0.50:
            is_ambiguous = "ambiguous" in selection.reasoning.lower()
            is_llm_error = "llm routing error" in selection.reasoning.lower() or "gemini" in selection.reasoning.lower() or "error" in selection.reasoning.lower()
            err = ErrorDetails(
                code="AI_ROUTING_ERROR" if is_llm_error else ("AMBIGUOUS_REQUEST" if is_ambiguous else "ROUTING_FAILED"),
                message=selection.reasoning if (is_ambiguous or is_llm_error) else "Unable to determine matching workflow from the request intent. Please refine your query."
            )
            return self._create_error_response(routing=selection, error=err, trace=trace)

        # 2. Input Validation phase
        workflow = self.registry.get_or_raise(selection.workflow_id)
        
        # Check strict missing inputs per workflow requirements
        missing_fields = []
        if workflow.id == "WF007":
            if not (inputs.get("campaign_goal") or inputs.get("goal")):
                missing_fields.append("Campaign goal")
            if not (inputs.get("dates") or inputs.get("timeline")):
                missing_fields.append("Dates")
        elif workflow.id == "WF005":
            if not (inputs.get("order_id") or inputs.get("customer_email") or inputs.get("identifier")) and "ord-" not in message.lower() and "@" not in message:
                missing_fields.append("Order ID or customer email")
        elif workflow.id == "WF004":
            if not (inputs.get("product_name") or inputs.get("name")) and not any(k in inputs for k in ["attributes", "category"]) and "keyboard" not in message.lower() and "mouse" not in message.lower() and "headphone" not in message.lower():
                missing_fields.append("Product name")
                missing_fields.append("Category / Attributes")

        if missing_fields:
            selection.missing_inputs = missing_fields
            err = ErrorDetails(
                code="MISSING_INPUT",
                message=f"Required inputs are missing for {workflow.id} ({workflow.name}): {', '.join(missing_fields)}.",
                details={"missing_inputs": missing_fields}
            )
            return self._create_error_response(routing=selection, error=err, trace=trace, workflow=workflow)

        # 3. Execution phase
        engine_res: WorkflowExecutionResult = self.engine.execute(
            workflow=workflow,
            input_data=inputs,
            trace=trace
        )

        wf_summary = WorkflowSummary(
            id=workflow.id,
            name=workflow.name,
            trigger=workflow.trigger,
            tools=workflow.tools,
            step_count=len(workflow.steps)
        )

        if not engine_res.success:
            err = ErrorDetails(
                code="EXECUTION_ERROR",
                message=engine_res.error or "Workflow execution failed during step processing.",
                details={"workflow_id": workflow.id}
            )
            return ExecuteResponse(
                success=False,
                workflow=wf_summary,
                routing=selection,
                execution=ExecutionSummary(
                    status="failed",
                    total_duration_ms=engine_res.total_duration_ms,
                    events_count=len(engine_res.trace),
                    trace=engine_res.trace
                ),
                result=engine_res.data,
                error=err
            )

        return ExecuteResponse(
            success=True,
            workflow=wf_summary,
            routing=selection,
            execution=ExecutionSummary(
                status="completed",
                total_duration_ms=engine_res.total_duration_ms,
                events_count=len(engine_res.trace),
                trace=engine_res.trace
            ),
            result=engine_res.data,
            error=None
        )

    def _create_error_response(
        self, 
        routing: WorkflowSelection, 
        error: ErrorDetails, 
        trace: ExecutionTrace,
        workflow: Optional[WorkflowDefinition] = None
    ) -> ExecuteResponse:
        trace.record(event_type="error", details={"error_code": error.code, "message": error.message})
        
        summary = None
        if workflow:
            summary = WorkflowSummary(
                id=workflow.id,
                name=workflow.name,
                trigger=workflow.trigger,
                tools=workflow.tools,
                step_count=len(workflow.steps)
            )

        return ExecuteResponse(
            success=False,
            workflow=summary,
            routing=routing,
            execution=ExecutionSummary(
                status="failed",
                total_duration_ms=trace.total_duration_ms,
                events_count=len(trace.events),
                trace=trace.to_list()
            ),
            result=None,
            error=error
        )
