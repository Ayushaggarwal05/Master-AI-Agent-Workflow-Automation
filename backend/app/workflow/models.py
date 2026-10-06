from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

class WorkflowDefinition(BaseModel):
    """
    Standard domain model representing a validated AI agent workflow definition
    loaded from the Excel source of truth.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "WF001",
                "name": "Inventory Restock Check",
                "trigger": "User asks which products need restocking.",
                "inputs": ["Product inventory CSV", "minimum stock threshold"],
                "steps": [
                    "Load inventory",
                    "compare current stock with minimum threshold",
                    "identify low-stock products",
                    "calculate reorder quantity",
                    "generate restock list"
                ],
                "decision": "If current_stock < minimum_stock, mark product for restock.",
                "tools": ["CSV reader", "calculator"],
                "output": "List products requiring restock with current stock, threshold, suggested reorder quantity."
            }
        }
    )

    id: str = Field(..., description="Unique workflow identifier, e.g. WF001")
    name: str = Field(..., description="Human-readable workflow name")
    trigger: str = Field(..., description="Intent/trigger condition initiating this workflow")
    inputs: List[str] = Field(default_factory=list, description="Required inputs or data sources")
    steps: List[str] = Field(default_factory=list, description="Ordered sequence of execution steps")
    decision: str = Field(..., description="Decision logic or conditional routing rule")
    tools: List[str] = Field(default_factory=list, description="Tools and capabilities utilized by this workflow")
    output: str = Field(..., description="Expected final result or artifacts produced")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional extensible metadata")

    @field_validator("id", mode="before")
    @classmethod
    def normalize_id(cls, v: Any) -> str:
        if not v or not str(v).strip():
            raise ValueError("Workflow ID cannot be empty.")
        return str(v).strip().upper()

    @field_validator("name", "trigger", "decision", "output", mode="before")
    @classmethod
    def strip_strings(cls, v: Any) -> str:
        if v is None:
            return ""
        return str(v).strip()


class WorkflowSummary(BaseModel):
    """Compact summary of a workflow for listing and router selection."""
    id: str
    name: str
    trigger: str
    tools: List[str]
    step_count: int


class WorkflowListResponse(BaseModel):
    """API response model for listing all available workflows."""
    total: int
    workflows: List[WorkflowDefinition]


class WorkflowDetailResponse(BaseModel):
    """API response model for a single workflow detail."""
    workflow: WorkflowDefinition


class HealthResponse(BaseModel):
    """API response model for service health check."""
    status: str
    version: str
    environment: str
    workflows_loaded: int
    excel_path: str
