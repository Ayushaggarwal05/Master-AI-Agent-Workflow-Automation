import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ExecutionEvent(BaseModel):
    """Structured representation of a single execution event within a workflow run."""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    type: str = Field(..., description="Event type: workflow_selected, step_started, tool_called, condition_evaluated, etc.")
    step: Optional[str] = Field(default=None, description="Current workflow step description")
    tool: Optional[str] = Field(default=None, description="Tool name invoked")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Payload, parameters, or evaluation result")
    elapsed_ms: Optional[float] = Field(default=None, description="Milliseconds since workflow start")


class ExecutionTrace:
    """Collects and organizes events during workflow routing and step-by-step execution."""

    def __init__(self):
        self.events: List[ExecutionEvent] = []
        self._start_time: float = time.perf_counter()

    def record(
        self, 
        event_type: str, 
        step: Optional[str] = None, 
        tool: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None
    ) -> ExecutionEvent:
        """Records an execution event into the trace log."""
        elapsed = round((time.perf_counter() - self._start_time) * 1000, 2)
        event = ExecutionEvent(
            type=event_type,
            step=step,
            tool=tool,
            details=details or {},
            elapsed_ms=elapsed
        )
        self.events.append(event)
        return event

    def to_list(self) -> List[Dict[str, Any]]:
        """Exports the trace events as a list of dictionaries."""
        return [e.model_dump() for e in self.events]

    @property
    def total_duration_ms(self) -> float:
        """Total execution duration in milliseconds."""
        return round((time.perf_counter() - self._start_time) * 1000, 2)
