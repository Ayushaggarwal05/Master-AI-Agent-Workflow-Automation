from typing import Any, Dict, List, Set
from pydantic import ValidationError
from backend.app.workflow.models import WorkflowDefinition

class WorkflowValidationError(Exception):
    """Exception raised when workflow validation fails."""
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.message = message
        self.errors = errors or [message]


class WorkflowValidator:
    """
    Validates raw workflow rows and collections of WorkflowDefinition objects
    to ensure data integrity, required fields, and unique identifiers.
    """
    
    REQUIRED_FIELDS = ["id", "name", "trigger", "steps", "tools", "output"]

    @classmethod
    def validate_raw_row(cls, row_data: Dict[str, Any], row_number: int) -> List[str]:
        """
        Validates raw row dictionary before parsing into WorkflowDefinition.
        Returns a list of validation error strings for the row.
        """
        errors = []
        
        # Check if entire row is empty
        non_empty_values = [v for v in row_data.values() if v is not None and str(v).strip() != ""]
        if not non_empty_values:
            return ["Empty row detected"]

        # Check required fields
        wf_id = row_data.get("id")
        if not wf_id or not str(wf_id).strip() or str(wf_id).strip().lower() == "nan":
            errors.append(f"Row {row_number}: Missing required field 'id'")

        wf_name = row_data.get("name")
        if not wf_name or not str(wf_name).strip() or str(wf_name).strip().lower() == "nan":
            errors.append(f"Row {row_number}: Missing required field 'name'")

        trigger = row_data.get("trigger")
        if not trigger or not str(trigger).strip() or str(trigger).strip().lower() == "nan":
            errors.append(f"Row {row_number}: Missing required field 'trigger'")

        steps = row_data.get("steps")
        if not steps or (isinstance(steps, str) and not steps.strip()):
            errors.append(f"Row {row_number}: Missing required field 'steps'")

        tools = row_data.get("tools")
        if not tools or (isinstance(tools, str) and not tools.strip()):
            errors.append(f"Row {row_number}: Missing required field 'tools'")

        output = row_data.get("output")
        if not output or not str(output).strip() or str(output).strip().lower() == "nan":
            errors.append(f"Row {row_number}: Missing required field 'output'")

        return errors

    @classmethod
    def validate_workflow_definition(cls, wf: WorkflowDefinition) -> List[str]:
        """Validates semantic integrity of a parsed WorkflowDefinition instance."""
        errors = []
        if not wf.id or not wf.id.strip():
            errors.append(f"Workflow ID is empty.")
        if not wf.name or not wf.name.strip():
            errors.append(f"Workflow '{wf.id}' has an empty name.")
        if not wf.trigger or not wf.trigger.strip():
            errors.append(f"Workflow '{wf.id}' has an empty trigger.")
        if not wf.steps:
            errors.append(f"Workflow '{wf.id}' must contain at least one valid step.")
        if not wf.tools:
            errors.append(f"Workflow '{wf.id}' must specify at least one tool.")
        if not wf.output or not wf.output.strip():
            errors.append(f"Workflow '{wf.id}' has an empty output specification.")
        return errors

    @classmethod
    def validate_workflow_collection(cls, workflows: List[WorkflowDefinition]) -> None:
        """
        Validates the entire list of workflows for collection-wide constraints
        such as duplicate IDs. Raises WorkflowValidationError if issues are found.
        """
        if not workflows:
            raise WorkflowValidationError("No valid workflows found in the collection.")

        errors: List[str] = []
        seen_ids: Set[str] = set()
        duplicate_ids: Set[str] = set()

        for wf in workflows:
            # Individual semantic validation
            wf_errors = cls.validate_workflow_definition(wf)
            errors.extend(wf_errors)

            # Duplicate ID check
            wf_id_upper = wf.id.upper()
            if wf_id_upper in seen_ids:
                duplicate_ids.add(wf_id_upper)
            seen_ids.add(wf_id_upper)

        if duplicate_ids:
            errors.append(f"Duplicate workflow IDs detected: {', '.join(sorted(duplicate_ids))}")

        if errors:
            raise WorkflowValidationError(
                f"Workflow collection validation failed with {len(errors)} error(s).",
                errors=errors
            )
