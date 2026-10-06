import re
from typing import Any, Dict, List, Optional
from backend.app.tools.base import BaseTool, ToolResult
from backend.app.workflow.conditions import ConditionEvaluator

def compute_token_similarity(text1: str, text2: str) -> float:
    """Computes Jaccard/N-gram token similarity between two strings (0.0 to 1.0)."""
    if not text1 or not text2:
        return 0.0
    tokens1 = set(re.findall(r"\w+", text1.lower()))
    tokens2 = set(re.findall(r"\w+", text2.lower()))
    if not tokens1 or not tokens2:
        return 0.0
    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))
    return intersection / union if union > 0 else 0.0


class TextSimilarityTool(BaseTool):
    name = "text_similarity"
    description = "Calculates lexical and semantic similarity between two text strings."

    def run(self, text_a: str, text_b: str, **kwargs) -> ToolResult:
        score = compute_token_similarity(text_a, text_b)
        return ToolResult(
            success=True,
            data={"similarity_score": round(score, 4)},
            message=f"Similarity score: {score:.2f}"
        )


class DuplicateProductDetectorTool(BaseTool):
    name = "duplicate_product_detector"
    description = "Scans a product list to detect exact SKU matches and attribute similarities."

    def run(self, products: List[Dict[str, Any]], **kwargs) -> ToolResult:
        duplicate_groups = []
        n = len(products)
        processed_pairs = set()

        for i in range(n):
            for j in range(i + 1, n):
                p1 = products[i]
                p2 = products[j]

                sku1 = str(p1.get("sku", "")).strip().upper()
                sku2 = str(p2.get("sku", "")).strip().upper()
                name1 = str(p1.get("name", "")).strip()
                name2 = str(p2.get("name", "")).strip()
                attr1 = str(p1.get("attributes", "")).strip()
                attr2 = str(p2.get("attributes", "")).strip()

                exact_sku = bool(sku1 and sku2 and sku1 == sku2)
                sim_name = compute_token_similarity(name1, name2)
                sim_attr = compute_token_similarity(attr1, attr2)
                combined_sim = max(sim_name, (sim_name * 0.6 + sim_attr * 0.4))

                eval_res = ConditionEvaluator.evaluate_duplicate_confidence(exact_sku, combined_sim)

                if eval_res.passed:
                    duplicate_groups.append({
                        "product_1": {"sku": sku1, "name": name1, "attributes": attr1},
                        "product_2": {"sku": sku2, "name": name2, "attributes": attr2},
                        "confidence": eval_res.details.get("confidence"),
                        "match_type": eval_res.action_taken,
                        "similarity_score": round(combined_sim, 2)
                    })

        return ToolResult(
            success=True,
            data={
                "total_products_checked": n,
                "duplicates_found_count": len(duplicate_groups),
                "duplicate_groups": duplicate_groups
            },
            message=f"Checked {n} products. Detected {len(duplicate_groups)} potential duplicate pairs."
        )
