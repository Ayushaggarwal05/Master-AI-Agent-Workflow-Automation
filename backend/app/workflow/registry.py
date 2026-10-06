from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from backend.app.core.logging import get_logger
from backend.app.workflow.models import WorkflowDefinition, WorkflowSummary
from backend.app.workflow.loader import ExcelWorkflowLoader

logger = get_logger(__name__)

class WorkflowNotFoundError(Exception):
    """Exception raised when a requested workflow ID does not exist in registry."""
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        super().__init__(f"Workflow with ID '{workflow_id}' not found in registry.")


class WorkflowRegistry:
    """
    In-memory registry storing loaded and validated WorkflowDefinition objects,
    indexed by their unique workflow ID.
    """

    def __init__(self):
        self._workflows: Dict[str, WorkflowDefinition] = {}
        self._source_path: Optional[Path] = None

    def load_from_excel(self, excel_path: Union[str, Path]) -> int:
        """
        Loads workflow definitions from an Excel file via ExcelWorkflowLoader
        and populates the internal registry.
        """
        path = Path(excel_path)
        loader = ExcelWorkflowLoader(path)
        definitions = loader.load()
        
        self.clear()
        for wf in definitions:
            self.register(wf)
            
        self._source_path = path
        logger.info(f"Registry populated with {len(self._workflows)} workflows from {path.name}")
        return len(self._workflows)

    def register(self, workflow: WorkflowDefinition) -> None:
        """Registers a single workflow definition into the registry."""
        wf_id = workflow.id.upper()
        if wf_id in self._workflows:
            logger.warning(f"Overwriting existing workflow definition for ID: {wf_id}")
        self._workflows[wf_id] = workflow

    def get(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Retrieves a workflow by its ID (case-insensitive). Returns None if not found."""
        return self._workflows.get(workflow_id.strip().upper())

    def get_or_raise(self, workflow_id: str) -> WorkflowDefinition:
        """Retrieves a workflow by its ID, raising WorkflowNotFoundError if missing."""
        wf = self.get(workflow_id)
        if not wf:
            raise WorkflowNotFoundError(workflow_id)
        return wf

    def list_all(self) -> List[WorkflowDefinition]:
        """Returns a list of all registered workflow definitions sorted by ID."""
        return sorted(self._workflows.values(), key=lambda w: w.id)

    def exists(self, workflow_id: str) -> bool:
        """Checks if a workflow ID exists in the registry."""
        return workflow_id.strip().upper() in self._workflows

    def count(self) -> int:
        """Returns the total number of registered workflows."""
        return len(self._workflows)

    def clear(self) -> None:
        """Clears all workflows from the registry."""
        self._workflows.clear()
        self._source_path = None

    def get_metadata_for_router(self) -> List[Dict[str, Any]]:
        """
        Provides compact, semantic metadata of all workflows specifically formatted
        for the Stage 2 AI Agent router to perform semantic matching.
        """
        metadata = []
        for wf in self.list_all():
            metadata.append({
                "id": wf.id,
                "name": wf.name,
                "trigger": wf.trigger,
                "inputs": wf.inputs,
                "tools": wf.tools,
                "decision": wf.decision,
                "output": wf.output,
                "step_count": len(wf.steps)
            })
        return metadata

    def get_summaries(self) -> List[WorkflowSummary]:
        """Returns lightweight summaries of all registered workflows."""
        return [
            WorkflowSummary(
                id=wf.id,
                name=wf.name,
                trigger=wf.trigger,
                tools=wf.tools,
                step_count=len(wf.steps)
            )
            for wf in self.list_all()
        ]

# Global singleton instance of the registry
_global_registry = WorkflowRegistry()

def get_workflow_registry() -> WorkflowRegistry:
    """Returns the shared WorkflowRegistry singleton."""
    return _global_registry
