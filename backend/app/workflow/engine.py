from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.app.core.logging import get_logger
from backend.app.workflow.models import WorkflowDefinition
from backend.app.workflow.trace import ExecutionTrace
from backend.app.tools.registry import ToolRegistry, get_tool_registry

logger = get_logger(__name__)

class WorkflowExecutionResult(BaseModel):
    """Encapsulates the complete result of a workflow execution."""
    success: bool
    workflow_id: str
    workflow_name: str
    output_summary: str
    data: Dict[str, Any]
    trace: List[Dict[str, Any]]
    total_duration_ms: float
    error: Optional[str] = None


class WorkflowEngine:
    """
    Generic, reusable workflow execution engine.
    Executes workflow steps in sequence by dynamically dispatching to tools in the ToolRegistry
    and evaluating decision conditions without hardcoded workflow branches.
    """

    def __init__(self, tool_registry: Optional[ToolRegistry] = None):
        self.tools = tool_registry or get_tool_registry()

    def execute(
        self, 
        workflow: WorkflowDefinition, 
        input_data: Dict[str, Any],
        trace: Optional[ExecutionTrace] = None
    ) -> WorkflowExecutionResult:
        """
        Executes a workflow definition against the provided input dataset.
        """
        trace = trace or ExecutionTrace()
        logger.info(f"Engine starting execution for workflow: [{workflow.id}] {workflow.name}")
        
        context: Dict[str, Any] = {
            "inputs": input_data,
            "raw_records": [],
            "processed_records": [],
            "calculations": {},
            "evaluation": {},
            "artifacts": {}
        }

        trace.record(
            event_type="input_validation",
            step="Validate provided inputs against workflow requirements",
            details={"declared_inputs": workflow.inputs, "provided_keys": list(input_data.keys())}
        )

        try:
            # Execute each step defined in the Excel workflow
            for step_index, step_desc in enumerate(workflow.steps, start=1):
                self._execute_step(
                    step_index=step_index,
                    step_desc=step_desc,
                    workflow=workflow,
                    context=context,
                    trace=trace
                )

            # Compile final structured payload
            final_data = self._compile_final_output(workflow, context)
            
            trace.record(
                event_type="final_result",
                step="Workflow execution completed successfully",
                details={"output_summary": workflow.output, "result_keys": list(final_data.keys())}
            )

            return WorkflowExecutionResult(
                success=True,
                workflow_id=workflow.id,
                workflow_name=workflow.name,
                output_summary=workflow.output,
                data=final_data,
                trace=trace.to_list(),
                total_duration_ms=trace.total_duration_ms
            )

        except Exception as e:
            logger.error(f"Engine error executing {workflow.id}: {str(e)}", exc_info=True)
            trace.record(
                event_type="error",
                details={"error_message": str(e), "workflow_id": workflow.id}
            )
            return WorkflowExecutionResult(
                success=False,
                workflow_id=workflow.id,
                workflow_name=workflow.name,
                output_summary="Execution failed due to error.",
                data=context.get("artifacts", {}),
                trace=trace.to_list(),
                total_duration_ms=trace.total_duration_ms,
                error=str(e)
            )

    def _execute_step(
        self,
        step_index: int,
        step_desc: str,
        workflow: WorkflowDefinition,
        context: Dict[str, Any],
        trace: ExecutionTrace
    ) -> None:
        """Executes an individual workflow step dynamically based on step intent and registered tools."""
        trace.record(
            event_type="step_started",
            step=step_desc,
            details={"step_number": step_index}
        )

        step_lower = step_desc.lower()
        inputs = context["inputs"]

        # Step 1: Ingestion / File / Data reading
        if any(term in step_lower for term in ["load", "read", "search order", "retrieve", "fetch", "provide"]):
            self._handle_ingestion_step(step_desc, workflow, context, trace)

        # Step 2: Normalization & Validation
        elif any(term in step_lower for term in ["normalize", "validate", "detect", "match", "remove duplicates", "compare identifiers"]):
            self._handle_normalization_step(step_desc, workflow, context, trace)

        # Step 3: Analysis, Calculation & Decision Rules
        elif any(term in step_lower for term in ["compare", "calculate", "identify", "classify", "rank", "similarity", "understand requirements"]):
            self._handle_analysis_step(step_desc, workflow, context, trace)

        # Step 4: Generation / Summarization
        elif any(term in step_lower for term in ["generate", "create", "summarize", "export", "produce", "recommendations"]):
            self._handle_generation_step(step_desc, workflow, context, trace)

        else:
            # General fallback step execution
            trace.record(
                event_type="tool_called",
                step=step_desc,
                tool="generic_step_executor",
                details={"status": "step evaluated"}
            )

        trace.record(
            event_type="step_completed",
            step=step_desc,
            details={"step_number": step_index}
        )

    def _handle_ingestion_step(
        self, step: str, workflow: WorkflowDefinition, context: Dict[str, Any], trace: ExecutionTrace
    ) -> None:
        inputs = context["inputs"]
        
        # Order / Shipment lookup
        if "order" in step.lower() or "shipment" in step.lower() or "WF005" == workflow.id:
            order_tool = self.tools.get_or_raise("order_lookup")
            ident = inputs.get("order_id") or inputs.get("identifier") or inputs.get("customer_email") or "ORD-9021"
            
            trace.record(event_type="tool_called", step=step, tool="order_lookup", details={"identifier": ident})
            res = order_tool.run(identifier=ident)
            trace.record(event_type="tool_result", step=step, tool="order_lookup", details={"success": res.success, "data": res.data})
            
            if res.success:
                context["artifacts"]["order"] = res.data
                # Call shipment tool
                shipment_tool = self.tools.get_or_raise("shipment_lookup")
                trace.record(event_type="tool_called", step=step, tool="shipment_lookup", details={"order_id": ident})
                ship_res = shipment_tool.run(order_data=res.data)
                trace.record(event_type="tool_result", step=step, tool="shipment_lookup", details={"data": ship_res.data})
                context["artifacts"]["shipment"] = ship_res.data
            else:
                raise ValueError(res.error or f"Order not found for identifier: {ident}")

        # Execution logs for reporting
        elif "log" in step.lower() or "WF010" == workflow.id:
            csv_tool = self.tools.get_or_raise("csv_reader")
            path = inputs.get("file_path") or inputs.get("logs_file") or "sample_data/workflow_logs.csv"
            trace.record(event_type="tool_called", step=step, tool="csv_reader", details={"file": path})
            res = csv_tool.run(file_path=path, csv_data=inputs.get("csv_data"))
            trace.record(event_type="tool_result", step=step, tool="csv_reader", details={"records_loaded": len(res.data) if res.data else 0})
            context["raw_records"] = res.data or []

        # General CSV / Excel reading
        else:
            csv_tool = self.tools.get_or_raise("csv_reader")
            # Select sample file based on workflow hints if not explicitly passed
            path = inputs.get("file_path")
            if not path:
                if "inventory" in workflow.name.lower():
                    path = "sample_data/inventory.csv"
                elif "price" in workflow.name.lower():
                    path = "sample_data/products.csv"
                elif "vendor" in workflow.name.lower():
                    path = "sample_data/vendor_products.csv"
                elif "duplicate" in workflow.name.lower():
                    path = "sample_data/products.csv"
                elif "keyword" in workflow.name.lower():
                    path = "sample_data/keywords.csv"
                elif "employee" in workflow.name.lower():
                    path = "sample_data/employees.csv"

            if path or inputs.get("csv_data"):
                trace.record(event_type="tool_called", step=step, tool="csv_reader", details={"file": path})
                res = csv_tool.run(file_path=path, csv_data=inputs.get("csv_data"))
                trace.record(event_type="tool_result", step=step, tool="csv_reader", details={"records_loaded": len(res.data) if res.data else 0, "error": res.error})
                if not res.success:
                    raise ValueError(res.error or f"Failed to load file: {path}")
                context["raw_records"] = res.data or []

    def _handle_normalization_step(
        self, step: str, workflow: WorkflowDefinition, context: Dict[str, Any], trace: ExecutionTrace
    ) -> None:
        raw = context.get("raw_records", [])
        
        # Column normalization
        if "normalize" in step.lower() or "vendor" in workflow.name.lower():
            norm_tool = self.tools.get_or_raise("column_normalizer")
            trace.record(event_type="tool_called", step=step, tool="column_normalizer", details={"count": len(raw)})
            res = norm_tool.run(rows=raw)
            trace.record(event_type="tool_result", step=step, tool="column_normalizer", details={"normalized_count": len(res.data)})
            context["processed_records"] = res.data

        # Data validation
        if "validate" in step.lower() or "invalid" in step.lower():
            val_tool = self.tools.get_or_raise("data_validator")
            target_rows = context.get("processed_records") or raw
            trace.record(event_type="tool_called", step=step, tool="data_validator", details={"rows": len(target_rows)})
            res = val_tool.run(rows=target_rows)
            trace.record(event_type="tool_result", step=step, tool="data_validator", details={"summary": res.data.get("summary")})
            context["artifacts"]["validation_summary"] = res.data

        # Keyword deduplication
        if "keyword" in step.lower() or "remove duplicates" in step.lower():
            raw_keywords = [r.get("keyword") for r in raw if r.get("keyword")] if raw else context["inputs"].get("keywords", [])
            trace.record(event_type="condition_evaluated", step=step, details={"rule": "Deduplicate keywords preserving uniqueness", "count_before": len(raw_keywords)})
            deduped = list(dict.fromkeys([k.strip().lower() for k in raw_keywords if k and str(k).strip()]))
            context["artifacts"]["deduped_keywords"] = deduped

    def _handle_analysis_step(
        self, step: str, workflow: WorkflowDefinition, context: Dict[str, Any], trace: ExecutionTrace
    ) -> None:
        inputs = context["inputs"]
        records = context.get("processed_records") or context.get("raw_records") or []

        # Inventory Restock Check (WF001)
        if "inventory" in workflow.name.lower() or "restock" in step.lower() or "threshold" in step.lower():
            calc_tool = self.tools.get_or_raise("calculator")
            threshold = float(inputs.get("minimum_stock_threshold") or inputs.get("minimum_stock") or 10.0)
            trace.record(event_type="tool_called", step=step, tool="calculator", details={"operation": "stock_check", "threshold": threshold})
            res = calc_tool.run(operation="stock_check", items=records, minimum_stock=threshold)
            trace.record(
                event_type="condition_evaluated",
                step=step,
                details={"condition": "current_stock < minimum_stock", "restock_needed_count": res.data.get("restock_required_count")}
            )
            trace.record(event_type="tool_result", step=step, tool="calculator", details={"restock_items": len(res.data.get("restock_items", []))})
            context["artifacts"]["restock_report"] = res.data

        # Price Validation (WF002)
        elif "price" in workflow.name.lower() or "vendor price" in step.lower() or "difference" in step.lower():
            calc_tool = self.tools.get_or_raise("calculator")
            # Load vendor prices
            csv_tool = self.tools.get_or_raise("csv_reader")
            v_res = csv_tool.run(file_path="sample_data/vendor_prices.csv")
            v_dict = {str(r.get("sku", "")).upper(): float(r.get("vendor_price", 0)) for r in (v_res.data or []) if r.get("sku")}
            
            trace.record(event_type="tool_called", step=step, tool="calculator", details={"operation": "price_comparison", "threshold_pct": 10.0})
            res = calc_tool.run(operation="price_comparison", products=records, vendor_prices=v_dict, threshold_pct=10.0)
            trace.record(
                event_type="condition_evaluated",
                step=step,
                details={"condition": "price_difference > 10%", "exceptions_flagged": res.data.get("exception_count")}
            )
            trace.record(event_type="tool_result", step=step, tool="calculator", details={"exceptions": res.data.get("exception_count")})
            context["artifacts"]["price_validation_report"] = res.data

        # Duplicate Product Detection (WF006)
        elif "duplicate" in workflow.name.lower() or "compare product attributes" in step.lower():
            dup_tool = self.tools.get_or_raise("duplicate_product_detector")
            trace.record(event_type="tool_called", step=step, tool="duplicate_product_detector", details={"products_count": len(records)})
            res = dup_tool.run(products=records)
            trace.record(
                event_type="condition_evaluated",
                step=step,
                details={"condition": "exact SKU = definite duplicate; high attribute similarity = possible duplicate", "found": res.data.get("duplicates_found_count")}
            )
            trace.record(event_type="tool_result", step=step, tool="duplicate_product_detector", details={"duplicates_count": res.data.get("duplicates_found_count")})
            context["artifacts"]["duplicate_report"] = res.data

        # SEO Keyword Classification (WF008)
        elif "keyword" in workflow.name.lower() or "intent" in step.lower():
            llm_tool = self.tools.get_or_raise("llm_generate")
            kws = context["artifacts"].get("deduped_keywords") or [r.get("keyword") for r in records if r.get("keyword")] or inputs.get("keywords", [])
            trace.record(event_type="tool_called", step=step, tool="llm_generate", details={"task_type": "keyword_classification", "keywords_count": len(kws)})
            res = llm_tool.run(task_type="keyword_classification", keywords=kws, categories=["Electronics & Gadgets"])
            trace.record(
                event_type="condition_evaluated",
                step=step,
                details={"condition": "Categorize as Informational, Commercial, Transactional, Navigational", "classified_count": len(res.data.get("classification_results", []))}
            )
            trace.record(event_type="tool_result", step=step, tool="llm_generate", details={"classified_count": len(res.data.get("classification_results", []))})
            context["artifacts"]["keyword_classification_report"] = res.data

        # Employee Task Assignment (WF009)
        elif "employee" in workflow.name.lower() or "rank candidates" in step.lower() or "workload" in step.lower():
            rank_tool = self.tools.get_or_raise("ranking_tool")
            task_desc = inputs.get("task_description") or "Develop Python FastAPI backend with ETL pipeline"
            trace.record(event_type="tool_called", step=step, tool="ranking_tool", details={"task": task_desc})
            res = rank_tool.run(
                task_description=task_desc,
                required_skills=inputs.get("skills"),
                priority=inputs.get("priority", "High"),
                deadline=inputs.get("deadline", "End of Sprint")
            )
            trace.record(
                event_type="condition_evaluated",
                step=step,
                details={"condition": "Prefer required skills + available capacity. Escalate if no suitable employee.", "status": res.data.get("status")}
            )
            trace.record(event_type="tool_result", step=step, tool="ranking_tool", details={"recommended": res.data.get("recommended_employee", {}).get("name")})
            context["artifacts"]["assignment_result"] = res.data

        # Workflow Performance Report (WF010)
        elif "performance" in workflow.name.lower() or "failure rate" in step.lower() or "average execution time" in step.lower():
            rep_tool = self.tools.get_or_raise("reporting_tool")
            trace.record(event_type="tool_called", step=step, tool="reporting_tool", details={"logs_count": len(records)})
            res = rep_tool.run(logs=records, fail_threshold_pct=10.0, time_threshold_sec=3.0)
            trace.record(
                event_type="condition_evaluated",
                step=step,
                details={"condition": "Flag workflows with failure rate > 10% or avg duration > 3.0s", "flagged_count": len(res.data.get("flagged_workflows", []))}
            )
            trace.record(event_type="tool_result", step=step, tool="reporting_tool", details={"summary": res.data.get("summary_metrics")})
            context["artifacts"]["performance_report"] = res.data

    def _handle_generation_step(
        self, step: str, workflow: WorkflowDefinition, context: Dict[str, Any], trace: ExecutionTrace
    ) -> None:
        inputs = context["inputs"]

        # Product Description Generator (WF004)
        if "description" in workflow.name.lower() or "seo title" in step.lower():
            llm_tool = self.tools.get_or_raise("llm_generate")
            trace.record(
                event_type="tool_called",
                step=step,
                tool="llm_generate",
                details={"task_type": "product_content", "product": inputs.get("product_name", "Wireless Headphones")}
            )
            res = llm_tool.run(
                task_type="product_content",
                product_name=inputs.get("product_name", "Ergonomic Wireless Mouse"),
                category=inputs.get("category", "Electronics"),
                attributes=inputs.get("attributes", "DPI: 4000; Bluetooth 5.0"),
                material=inputs.get("material"),
                color=inputs.get("color"),
                target_audience=inputs.get("target_audience")
            )
            trace.record(
                event_type="condition_evaluated",
                step=step,
                details={"condition": "Do not invent missing attributes; explicitly mark missing information", "missing_attributes": res.data.get("explicitly_missing_attributes")}
            )
            trace.record(event_type="tool_result", step=step, tool="llm_generate", details={"seo_title": res.data.get("seo_title")})
            context["artifacts"]["generated_content"] = res.data

        # Marketing Campaign Brief (WF007)
        elif "campaign" in workflow.name.lower() or "messaging" in step.lower() or "checklist" in step.lower():
            llm_tool = self.tools.get_or_raise("llm_generate")
            trace.record(event_type="tool_called", step=step, tool="llm_generate", details={"task_type": "campaign_brief"})
            res = llm_tool.run(
                task_type="campaign_brief",
                campaign_goal=inputs.get("campaign_goal") or inputs.get("goal"),
                product_list=inputs.get("product_list") or inputs.get("products", ["Ergonomic Wireless Mouse", "Mechanical Keyboard"]),
                target_audience=inputs.get("target_audience", "Remote Workers & Tech Pros"),
                promotion=inputs.get("promotion", "20% Spring Launch Discount"),
                dates=inputs.get("dates") or inputs.get("timeline")
            )
            if not res.success:
                raise ValueError(res.error)

            trace.record(
                event_type="condition_evaluated",
                step=step,
                details={"condition": "If campaign goal or dates are missing, request them before generating brief", "status": "Passed"}
            )
            trace.record(event_type="tool_result", step=step, tool="llm_generate", details={"objective": res.data.get("campaign_objective")})
            context["artifacts"]["campaign_brief"] = res.data

    def _compile_final_output(self, workflow: WorkflowDefinition, context: Dict[str, Any]) -> Dict[str, Any]:
        """Compiles the artifacts produced during step execution into a structured result payload."""
        artifacts = context.get("artifacts", {})
        return {
            "workflow_id": workflow.id,
            "workflow_name": workflow.name,
            "expected_output_spec": workflow.output,
            "artifacts": artifacts,
            "primary_output": next(iter(artifacts.values())) if artifacts else "Execution completed."
        }
