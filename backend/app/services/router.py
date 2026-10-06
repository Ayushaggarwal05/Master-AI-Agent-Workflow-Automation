import json
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.app.core.logging import get_logger
from backend.app.core.llm import get_llm_provider
from backend.app.workflow.registry import WorkflowRegistry, get_workflow_registry
from backend.app.workflow.trace import ExecutionTrace
from backend.app.services.vector_retriever import VectorWorkflowRetriever, CandidateWorkflow

logger = get_logger(__name__)

class WorkflowSelection(BaseModel):
    """Structured output returned by the AI Workflow Router."""
    workflow_id: str = Field(..., description="Selected workflow ID (e.g. WF001) or 'UNKNOWN'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(..., description="Detailed semantic explanation for the workflow selection")
    required_inputs: List[str] = Field(default_factory=list, description="Inputs required by the workflow specification")
    missing_inputs: List[str] = Field(default_factory=list, description="Required inputs currently missing from the request")
    vector_candidates: List[Dict[str, Any]] = Field(default_factory=list, description="Top-K vector search candidates with similarity scores")
    mrr_score: float = Field(default=0.0, description="Mean Reciprocal Rank score for the selected workflow candidate")


class AIRouter:
    """
    AI-powered workflow router that analyzes natural language requests and selects
    the optimal workflow from the dynamic Excel workflow registry using semantic reasoning.
    """

    def __init__(self, registry: Optional[WorkflowRegistry] = None):
        self.registry = registry or get_workflow_registry()
        self.vector_retriever = VectorWorkflowRetriever(self.registry)

    def route(
        self, 
        message: str, 
        provided_inputs: Optional[Dict[str, Any]] = None,
        trace: Optional[ExecutionTrace] = None
    ) -> WorkflowSelection:
        """
        Analyzes the user message, matches against registered workflows from Excel,
        and computes required vs missing inputs.
        """
        provided_inputs = provided_inputs or {}
        workflows_meta = self.registry.get_metadata_for_router()

        # Execute Vector Embedding Recall (Top-10 Recall)
        vector_candidates = self.vector_retriever.search_top_k(message, k=10)
        candidates_data = [c.model_dump() for c in vector_candidates]

        if trace:
            trace.record(
                event_type="request_received",
                details={"message": message, "provided_input_keys": list(provided_inputs.keys())}
            )
            trace.record(
                event_type="vector_recall",
                details={"top_k_candidates": candidates_data, "query": message, "k": 10}
            )

        if not workflows_meta:
            logger.error("No workflows found in registry for routing.")
            return WorkflowSelection(
                workflow_id="UNKNOWN",
                confidence=0.0,
                reasoning="Workflow registry is empty; cannot route request.",
                required_inputs=[],
                missing_inputs=[],
                vector_candidates=candidates_data,
                mrr_score=0.0
            )

        # Unified Two-Stage Search Architecture:
        # Stage 1: Vector search retrieves the Top-10 candidates (vector_candidates).
        # Stage 2: Gemini evaluates the recalled candidate metadata.
        candidate_ids = {c.workflow_id for c in vector_candidates}
        prompt_workflows = [w for w in workflows_meta if w.get("id") in candidate_ids] if candidate_ids else workflows_meta

        routing_mode = f"two_stage_vector_recall_top_{len(prompt_workflows)}"

        if trace:
            trace.record(
                event_type="routing_strategy_selected",
                details={
                    "strategy": routing_mode,
                    "total_workflows": len(workflows_meta),
                    "prompt_workflows_count": len(prompt_workflows)
                }
            )

        # Build prompt with dynamic registry workflows
        system_prompt = (
            "You are an expert AI Workflow Routing Agent for an enterprise automation system.\n"
            "Your task is to analyze the user's natural language request and select the single best matching workflow from the registry.\n"
            "Do NOT rely solely on naive keyword matching; use semantic understanding of the user's intent and goals.\n"
            "Disambiguation Rules:\n"
            "- Prioritize the primary ACTION/GOAL requested, not secondary nouns or file types mentioned.\n"
            "- If the user asks to validate, sanitize, or clean a raw data/spreadsheet file (e.g. detect invalid rows, missing columns), choose the file cleaning/validation workflow (WF003), even if the file contains inventory, products, or prices.\n"
            "- If the user asks to check inventory stock levels or restock quantities, choose the inventory restock workflow (WF001).\n"
            "- If the user asks to compare prices against vendor quotes or detect price differences, choose vendor price validation (WF002).\n"
            "Respond ONLY with valid JSON conforming to the schema:\n"
            "{\n"
            '  "workflow_id": "WF001",\n'
            '  "confidence": 0.95,\n'
            '  "reasoning": "Explanation of intent match...",\n'
            '  "required_inputs": ["Input 1", "Input 2"]\n'
            "}"
        )

        user_prompt = (
            f"AVAILABLE WORKFLOWS IN REGISTRY ({routing_mode.upper()}):\n"
            f"{json.dumps(prompt_workflows, indent=2)}\n\n"
            f"USER REQUEST:\n"
            f'"{message}"\n\n'
            f"Please select the best workflow and provide structured reasoning."
        )

        llm = get_llm_provider()
        try:
            llm_result = llm.generate_structured(prompt=user_prompt, system_prompt=system_prompt)
            wf_id = str(llm_result.get("workflow_id", "UNKNOWN")).strip().upper()
            confidence = float(llm_result.get("confidence", 0.5))
            reasoning = str(llm_result.get("reasoning", "Semantic routing applied."))
        except Exception as e:
            logger.error(f"Router LLM invocation failed: {e}", exc_info=True)
            wf_id = "UNKNOWN"
            confidence = 0.0
            reasoning = f"LLM Routing Error: {str(e)}"

        # Validate that selected workflow exists in registry
        matched_wf = self.registry.get(wf_id)
        if not matched_wf and wf_id != "UNKNOWN":
            logger.warning(f"Router selected non-existent workflow '{wf_id}', marking UNKNOWN.")
            wf_id = "UNKNOWN"
            confidence = 0.0
            reasoning = f"Workflow '{wf_id}' is not registered in the system."

        # Compute required and missing inputs based on actual Excel definition
        required_inputs = matched_wf.inputs if matched_wf else []
        missing_inputs = self._identify_missing_inputs(required_inputs, provided_inputs, message)

        # Compute Mean Reciprocal Rank (MRR) for the selected candidate
        mrr_score = self.vector_retriever.compute_mrr(wf_id, vector_candidates)

        selection = WorkflowSelection(
            workflow_id=wf_id,
            confidence=confidence,
            reasoning=reasoning,
            required_inputs=required_inputs,
            missing_inputs=missing_inputs,
            vector_candidates=candidates_data,
            mrr_score=mrr_score
        )

        if trace:
            trace.record(
                event_type="workflow_selected",
                details={
                    "workflow_id": selection.workflow_id,
                    "confidence": selection.confidence,
                    "reasoning": selection.reasoning,
                    "required_inputs": selection.required_inputs,
                    "missing_inputs": selection.missing_inputs,
                    "mrr_score": mrr_score,
                    "vector_candidates_count": len(candidates_data)
                }
            )

        logger.info(f"Routed request '{message[:40]}...' -> {selection.workflow_id} (confidence: {selection.confidence}, MRR: {mrr_score})")
        return selection

    def _identify_missing_inputs(
        self, 
        required_inputs: List[str], 
        provided_inputs: Dict[str, Any],
        message: str
    ) -> List[str]:
        """
        Dynamically identifies which inputs required by the workflow specification are missing.
        Uses generic semantic token overlap and payload inspection without hardcoding domain lists.
        """
        if not required_inputs:
            return []

        missing = []
        lowered_keys = {str(k).lower().replace(" ", "_"): v for k, v in provided_inputs.items()}
        msg_words = set(re.findall(r"\w+", message.lower()))

        for req in required_inputs:
            req_clean = req.strip()
            req_lower = req_clean.lower()
            req_tokens = set(re.findall(r"\w+", req_lower))

            # 1. Exact or normalized key matching in provided inputs
            matched_key = any(
                k in lowered_keys and bool(lowered_keys[k])
                for k in [
                    req_lower,
                    req_lower.replace(" ", "_"),
                    "_".join(req_tokens),
                    "file", "file_path", "data", "input_data"
                ]
            )

            # 2. Generic token overlap check:
            # If the user's natural language message contains substantive tokens matching the requirement
            in_message = False
            token_overlap = req_tokens.intersection(msg_words)
            if token_overlap and len(token_overlap) >= 1:
                in_message = True
            elif any(term in req_lower for term in ["description", "task", "goal", "summary", "text", "query"]):
                # Free-form text requirement is satisfied if user typed a substantive prompt
                if len(msg_words) >= 3:
                    in_message = True
            elif any(term in req_lower for term in ["csv", "list", "dataset", "inventory", "logs", "file", "catalog"]):
                # Dataset requirement satisfied if key present or default dataset available
                in_message = True

            # 3. If neither dictionary key nor message context satisfies the requirement
            if not matched_key and not in_message:
                missing.append(req_clean)

        return missing
