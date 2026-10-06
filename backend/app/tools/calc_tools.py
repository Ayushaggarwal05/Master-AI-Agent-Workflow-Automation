from typing import Any, Dict, List, Optional
from backend.app.tools.base import BaseTool, ToolResult
from backend.app.workflow.conditions import ConditionEvaluator

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Performs mathematical calculations, percentage comparisons, and threshold logic."

    def run(self, operation: str = "custom", **kwargs) -> ToolResult:
        if operation == "stock_check":
            items = kwargs.get("items", [])
            default_threshold = float(kwargs.get("minimum_stock", 10.0))
            
            restock_list = []
            adequate_list = []
            
            for item in items:
                curr = float(item.get("current_stock", item.get("stock", 0)))
                thresh = float(item.get("minimum_stock", default_threshold))
                
                cond = ConditionEvaluator.evaluate_stock_threshold(curr, thresh)
                enriched = {
                    "sku": item.get("sku", ""),
                    "name": item.get("name", item.get("product_name", "")),
                    "current_stock": curr,
                    "minimum_stock": thresh,
                    "needs_restock": cond.passed,
                    "suggested_reorder_qty": cond.details.get("reorder_qty", 0)
                }
                if cond.passed:
                    restock_list.append(enriched)
                else:
                    adequate_list.append(enriched)

            return ToolResult(
                success=True,
                data={
                    "total_inspected": len(items),
                    "restock_required_count": len(restock_list),
                    "restock_items": restock_list,
                    "adequate_items": adequate_list
                },
                message=f"Identified {len(restock_list)} items requiring restocking."
            )

        elif operation == "price_comparison":
            products = kwargs.get("products", [])
            vendor_prices = kwargs.get("vendor_prices", {})
            threshold_pct = float(kwargs.get("threshold_pct", 10.0))

            matched_products = []
            exceptions = []

            for p in products:
                sku = str(p.get("sku", "")).strip().upper()
                internal_price = float(p.get("unit_price", p.get("price", 0)))
                vendor_price = float(vendor_prices.get(sku, 0))

                if vendor_price > 0:
                    eval_res = ConditionEvaluator.evaluate_price_variance(
                        internal_price, vendor_price, threshold_pct
                    )
                    record = {
                        "sku": sku,
                        "name": p.get("name", ""),
                        "internal_price": internal_price,
                        "vendor_price": vendor_price,
                        "difference_pct": eval_res.details.get("diff_pct"),
                        "is_exception": eval_res.passed
                    }
                    matched_products.append(record)
                    if eval_res.passed:
                        exceptions.append(record)

            return ToolResult(
                success=True,
                data={
                    "total_matched": len(matched_products),
                    "exception_count": len(exceptions),
                    "matched_products": matched_products,
                    "exceptions": exceptions
                },
                message=f"Compared {len(matched_products)} SKUs. Found {len(exceptions)} price variance exceptions (> {threshold_pct}%)."
            )

        return ToolResult(success=True, data="Calculator completed.")
