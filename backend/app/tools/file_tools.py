import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from backend.app.core.config import settings
from backend.app.tools.base import BaseTool, ToolResult
from backend.app.workflow.conditions import ConditionEvaluator

def _resolve_file_path(file_path: Union[str, Path]) -> Path:
    """Helper to locate file in CWD, sample_data, or project root."""
    p = Path(file_path)
    if p.exists():
        return p.resolve()
        
    candidates = [
        settings.PROJECT_ROOT / "sample_data" / p.name,
        settings.BACKEND_DIR / "sample_data" / p.name,
        settings.PROJECT_ROOT / p,
        settings.BACKEND_DIR / p,
        Path.cwd() / "sample_data" / p.name
    ]
    for c in candidates:
        if c.exists():
            return c.resolve()
    return p.resolve()


class CSVReaderTool(BaseTool):
    name = "csv_reader"
    description = "Reads a CSV file or CSV string and returns a list of row dictionaries."

    def run(self, file_path: Optional[str] = None, csv_data: Optional[str] = None, **kwargs) -> ToolResult:
        try:
            if csv_data:
                import io
                df = pd.read_csv(io.StringIO(csv_data))
            elif file_path:
                resolved = _resolve_file_path(file_path)
                if not resolved.exists():
                    return ToolResult(success=False, error=f"CSV file not found: {file_path}")
                df = pd.read_csv(resolved)
            else:
                return ToolResult(success=False, error="Neither file_path nor csv_data provided to csv_reader.")

            records = df.fillna("").to_dict(orient="records")
            return ToolResult(
                success=True,
                data=records,
                message=f"Successfully loaded {len(records)} records from CSV."
            )
        except Exception as e:
            return ToolResult(success=False, error=f"CSV read error: {str(e)}")


class ExcelReaderTool(BaseTool):
    name = "excel_reader"
    description = "Reads an Excel file (.xlsx) and returns row dictionaries."

    def run(self, file_path: str, sheet_name: Optional[str] = None, **kwargs) -> ToolResult:
        try:
            resolved = _resolve_file_path(file_path)
            if not resolved.exists():
                return ToolResult(success=False, error=f"Excel file not found: {file_path}")
                
            df = pd.read_excel(resolved, sheet_name=sheet_name or 0, engine="openpyxl")
            records = df.fillna("").to_dict(orient="records")
            return ToolResult(
                success=True,
                data=records,
                message=f"Successfully loaded {len(records)} rows from Excel."
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Excel read error: {str(e)}")


class ColumnNormalizerTool(BaseTool):
    name = "column_normalizer"
    description = "Normalizes column names in a dataset to snake_case and canonical aliases."

    def run(self, rows: List[Dict[str, Any]], **kwargs) -> ToolResult:
        if not rows:
            return ToolResult(success=True, data=[])

        normalized_rows = []
        for r in rows:
            new_row = {}
            for k, v in r.items():
                clean_k = str(k).strip().lower().replace(" ", "_").replace("-", "_")
                # Canonical mapping
                if clean_k in ("vendor_sku", "product_sku", "item_sku"):
                    clean_k = "sku"
                elif clean_k in ("product_title", "product_name", "item_name", "title"):
                    clean_k = "name"
                elif clean_k in ("unit_price", "price_usd", "cost"):
                    clean_k = "price"
                elif clean_k in ("quantity_in_stock", "qty", "stock"):
                    clean_k = "stock"
                new_row[clean_k] = v
            normalized_rows.append(new_row)

        return ToolResult(
            success=True,
            data=normalized_rows,
            message=f"Normalized columns for {len(normalized_rows)} rows."
        )


class DataValidatorTool(BaseTool):
    name = "data_validator"
    description = "Validates row items against schema rules, splitting into valid and invalid rows."

    def run(self, rows: List[Dict[str, Any]], **kwargs) -> ToolResult:
        valid_rows = []
        invalid_rows = []

        for idx, row in enumerate(rows, start=1):
            eval_res = ConditionEvaluator.evaluate_vendor_row_validity(row)
            if eval_res.passed:
                valid_rows.append(row)
            else:
                invalid_rows.append({
                    "row_index": idx,
                    "row_data": row,
                    "reason": eval_res.action_taken,
                    "missing": eval_res.details.get("missing_fields", [])
                })

        return ToolResult(
            success=True,
            data={
                "valid_count": len(valid_rows),
                "invalid_count": len(invalid_rows),
                "valid_rows": valid_rows,
                "invalid_rows": invalid_rows,
                "summary": f"Processed {len(rows)} rows: {len(valid_rows)} valid, {len(invalid_rows)} invalid."
            }
        )
