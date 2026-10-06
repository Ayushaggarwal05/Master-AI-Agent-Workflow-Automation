from typing import Any, Dict, Optional
from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from backend.app.services.orchestrator import AgentOrchestrator, ExecuteResponse

router = APIRouter(tags=["Execution"])

class ExecuteRequest(BaseModel):
    """Payload for submitting a user request for AI workflow routing and execution."""
    message: str = Field(..., description="Natural language prompt or query from user")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Optional explicit input parameters, file paths, or payload data")
    workflow_id: Optional[str] = Field(default=None, description="Optional workflow ID to bypass routing and execute directly")


@router.post(
    "/execute",
    response_model=ExecuteResponse,
    summary="Execute AI Agent Workflow",
    description="Analyzes user intent with AI Router, selects workflow from Excel registry, executes steps through generic engine, and returns structured results with full execution trace."
)
async def execute_workflow(payload: ExecuteRequest):
    orchestrator = AgentOrchestrator()
    response = orchestrator.run(
        message=payload.message,
        inputs=payload.inputs,
        workflow_id=payload.workflow_id
    )
    return response
