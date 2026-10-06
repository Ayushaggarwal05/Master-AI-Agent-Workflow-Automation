import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import openpyxl
import pandas as pd

from backend.app.core.logging import get_logger
from backend.app.workflow.models import WorkflowDefinition
from backend.app.workflow.validator import WorkflowValidator, WorkflowValidationError
from backend.app.utils.parsers import parse_delimited_list

logger = get_logger(__name__)

# Column aliases mapping common variations to canonical model fields
COLUMN_ALIASES: Dict[str, str] = {
    "workflow_id": "id",
    "workflow id": "id",
    "id": "id",
    "wfid": "id",
    "workflow_name": "name",
    "workflow name": "name",
    "name": "name",
    "title": "name",
    "trigger": "trigger",
    "trigger condition": "trigger",
    "inputs": "inputs",
    "input": "inputs",
    "input data": "inputs",
    "steps": "steps",
    "step": "steps",
    "execution steps": "steps",
    "decision": "decision",
    "decision logic": "decision",
    "decision rule": "decision",
    "rules": "decision",
    "tools": "tools",
    "tool": "tools",
    "required tools": "tools",
    "output": "output",
    "expected output": "output",
    "outputs": "output",
    "result": "output"
}

class ExcelWorkflowLoader:
    """
    Excel loader responsible for reading workflow definitions from an Excel spreadsheet,
    normalizing headers and values, parsing multi-value columns, and validating
    the resulting domain objects.
    """

    def __init__(self, excel_path: Union[str, Path]):
        self.excel_path = Path(excel_path)

    def load(self, sheet_name: Optional[str] = None) -> List[WorkflowDefinition]:
        """
        Loads and validates all workflow definitions from the configured Excel file.
        Raises FileNotFoundError if file is missing, or WorkflowValidationError if malformed.
        """
        if not self.excel_path.exists():
            error_msg = f"Workflow Excel file not found at path: {self.excel_path.resolve()}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(f"Loading workflows from Excel file: {self.excel_path.resolve()}")
        
        try:
            # Read workbook using openpyxl directly or pandas
            df = pd.read_excel(
                self.excel_path,
                sheet_name=sheet_name if sheet_name else 0,
                dtype=str,
                engine="openpyxl"
            )
        except Exception as e:
            error_msg = f"Failed to read Excel file at {self.excel_path}: {str(e)}"
            logger.error(error_msg)
            raise WorkflowValidationError(error_msg)

        if df.empty:
            error_msg = f"Excel sheet at {self.excel_path} is empty."
            logger.error(error_msg)
            raise WorkflowValidationError(error_msg)

        # Normalize column names
        normalized_df = self._normalize_columns(df)
        
        # Parse rows into WorkflowDefinition instances
        workflows: List[WorkflowDefinition] = []
        validation_errors: List[str] = []

        for idx, row in normalized_df.iterrows():
            row_number = idx + 2 # Accounting for 0-index and header row
            row_dict = row.to_dict()

            # Skip completely empty rows
            non_empty_items = [v for v in row_dict.values() if pd.notna(v) and str(v).strip() != ""]
            if not non_empty_items:
                continue

            # Validate raw row fields
            row_errors = WorkflowValidator.validate_raw_row(row_dict, row_number)
            if row_errors:
                validation_errors.extend(row_errors)
                continue

            try:
                # Parse structured fields
                parsed_inputs = parse_delimited_list(row_dict.get("inputs"))
                parsed_steps = parse_delimited_list(row_dict.get("steps"))
                parsed_tools = parse_delimited_list(row_dict.get("tools"))

                decision_val = str(row_dict.get("decision", "")).strip()
                if decision_val.lower() in ("nan", "none", "null"):
                    decision_val = ""

                output_val = str(row_dict.get("output", "")).strip()

                wf_def = WorkflowDefinition(
                    id=str(row_dict["id"]).strip(),
                    name=str(row_dict["name"]).strip(),
                    trigger=str(row_dict["trigger"]).strip(),
                    inputs=parsed_inputs,
                    steps=parsed_steps,
                    decision=decision_val,
                    tools=parsed_tools,
                    output=output_val,
                    metadata={"source_row": row_number, "source_file": str(self.excel_path.name)}
                )
                workflows.append(wf_def)
            except Exception as ex:
                validation_errors.append(f"Row {row_number}: Unexpected error parsing row - {str(ex)}")

        if validation_errors:
            logger.error(f"Excel validation failed with {len(validation_errors)} error(s).")
            raise WorkflowValidationError(
                f"Failed to load workflows due to {len(validation_errors)} validation errors.",
                errors=validation_errors
            )

        # Validate whole collection
        WorkflowValidator.validate_workflow_collection(workflows)
        
        logger.info(f"Successfully loaded and validated {len(workflows)} workflows from Excel.")
        return workflows

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Maps spreadsheet column names to standard canonical names using COLUMN_ALIASES."""
        mapped_cols = {}
        for col in df.columns:
            clean_col = str(col).strip().lower()
            mapped = COLUMN_ALIASES.get(clean_col)
            if mapped:
                mapped_cols[col] = mapped
            else:
                # Keep original lowercased column
                mapped_cols[col] = clean_col

        df_renamed = df.rename(columns=mapped_cols)
        
        # Check that essential columns exist in dataframe
        missing_headers = []
        for req in ["id", "name", "trigger", "steps", "tools", "output"]:
            if req not in df_renamed.columns:
                missing_headers.append(req)

        if missing_headers:
            raise WorkflowValidationError(
                f"Excel sheet is missing required columns: {', '.join(missing_headers)}. Found columns: {list(df.columns)}"
            )

        return df_renamed
