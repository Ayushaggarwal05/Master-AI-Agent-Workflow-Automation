from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ConditionResult(BaseModel):
    """Result of evaluating a workflow decision rule or threshold condition."""
    rule: str
    passed: bool
    evaluated_value: Any
    details: Dict[str, Any] = Field(default_factory=dict)
    action_taken: Optional[str] = None


class ConditionEvaluator:
    """
    Evaluates workflow decision rules and conditions deterministically.
    Supports numerical thresholds, missing-field constraints, and categorization rules.
    """

    @staticmethod
    def evaluate_stock_threshold(current_stock: float, minimum_stock: float) -> ConditionResult:
        """WF001: If current_stock < minimum_stock, mark product for restock."""
        needs_restock = current_stock < minimum_stock
        reorder_qty = max(0.0, (minimum_stock * 2) - current_stock) if needs_restock else 0.0
        return ConditionResult(
            rule="current_stock < minimum_stock",
            passed=needs_restock,
            evaluated_value={"current_stock": current_stock, "minimum_stock": minimum_stock},
            action_taken="Mark for restock" if needs_restock else "Stock adequate",
            details={"reorder_qty": reorder_qty}
        )

    @staticmethod
    def evaluate_price_variance(internal_price: float, vendor_price: float, threshold_pct: float = 10.0) -> ConditionResult:
        """WF002: Flag if price difference > 10%."""
        if internal_price == 0:
            diff_pct = 100.0 if vendor_price > 0 else 0.0
        else:
            diff_pct = round(abs(vendor_price - internal_price) / internal_price * 100.0, 2)
            
        is_exception = diff_pct > threshold_pct
        return ConditionResult(
            rule=f"abs(vendor_price - internal_price) / internal_price > {threshold_pct}%",
            passed=is_exception,
            evaluated_value=diff_pct,
            action_taken="Flag exception (>10% diff)" if is_exception else "Price match within threshold",
            details={"diff_pct": diff_pct, "threshold_pct": threshold_pct}
        )

    @staticmethod
    def evaluate_vendor_row_validity(row: Dict[str, Any]) -> ConditionResult:
        """WF003: Rows missing SKU or product name are invalid."""
        # Find SKU key
        sku_val = next((row[k] for k in row if "sku" in k.lower() and row[k]), None)
        # Find product name / title key
        name_val = next((row[k] for k in row if any(term in k.lower() for term in ["name", "title", "product"]) and "sku" not in k.lower() and row[k]), None)

        is_valid = bool(sku_val and str(sku_val).strip() and name_val and str(name_val).strip())
        missing = []
        if not sku_val or not str(sku_val).strip():
            missing.append("SKU")
        if not name_val or not str(name_val).strip():
            missing.append("Product Name")

        return ConditionResult(
            rule="row must contain non-empty SKU and product name",
            passed=is_valid,
            evaluated_value={"sku": sku_val, "name": name_val},
            action_taken="Valid row" if is_valid else f"Invalid row: missing {', '.join(missing)}",
            details={"missing_fields": missing}
        )

    @staticmethod
    def evaluate_duplicate_confidence(exact_sku_match: bool, text_similarity_score: float) -> ConditionResult:
        """WF006: Exact SKU match = definite duplicate; High attribute similarity = possible duplicate."""
        if exact_sku_match:
            confidence = 1.0
            category = "Definite Duplicate (Exact SKU)"
        elif text_similarity_score >= 0.80:
            confidence = round(text_similarity_score, 2)
            category = "Definite Duplicate (High Attribute Similarity)"
        elif text_similarity_score >= 0.50:
            confidence = round(text_similarity_score, 2)
            category = "Possible Duplicate"
        else:
            confidence = round(text_similarity_score, 2)
            category = "Unique Product"

        is_dup = confidence >= 0.50
        return ConditionResult(
            rule="exact SKU match = definite duplicate; similarity >= 0.5 = possible duplicate",
            passed=is_dup,
            evaluated_value=confidence,
            action_taken=category,
            details={"confidence": confidence, "similarity": text_similarity_score, "is_duplicate": is_dup}
        )

    @staticmethod
    def evaluate_workflow_performance(failure_rate_pct: float, avg_duration_sec: float, fail_threshold: float = 10.0, time_threshold: float = 3.0) -> ConditionResult:
        """WF010: Flag workflows with failure rate > 10% or avg duration above threshold."""
        high_failure = failure_rate_pct > fail_threshold
        slow_steps = avg_duration_sec > time_threshold
        flagged = high_failure or slow_steps

        issues = []
        if high_failure:
            issues.append(f"Failure rate ({failure_rate_pct:.1f}%) exceeds {fail_threshold}%")
        if slow_steps:
            issues.append(f"Avg execution time ({avg_duration_sec:.2f}s) exceeds {time_threshold}s")

        return ConditionResult(
            rule="failure_rate > 10% OR avg_duration > threshold",
            passed=flagged,
            evaluated_value={"failure_rate_pct": failure_rate_pct, "avg_duration_sec": avg_duration_sec},
            action_taken="Flagged for Optimization" if flagged else "Healthy Workflow",
            details={"issues": issues, "flagged": flagged}
        )
