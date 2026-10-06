import math
import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from backend.app.core.logging import get_logger
from backend.app.workflow.models import WorkflowDefinition
from backend.app.workflow.registry import WorkflowRegistry, get_workflow_registry

logger = get_logger(__name__)


class CandidateWorkflow(BaseModel):
    """Represents a retrieved workflow candidate with vector similarity metrics."""
    workflow_id: str
    name: str
    trigger: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    rank: int
    reciprocal_rank: float


class VectorWorkflowRetriever:
    """
    Vector-based Semantic Workflow Retriever.
    Indexes all registered workflows using dense term-frequency / cosine vector embeddings
    to perform fast Top-K Candidate Recall and compute Mean Reciprocal Rank (MRR).
    """

    def __init__(self, registry: Optional[WorkflowRegistry] = None):
        self.registry = registry or get_workflow_registry()
        self._vector_index: Dict[str, Dict[str, float]] = {}
        self._doc_lengths: Dict[str, float] = {}
        self._idf: Dict[str, float] = {}
        self._build_index()

    def _tokenize(self, text: str) -> List[str]:
        """Normalizes and tokenizes text into distinct n-gram tokens."""
        if not text:
            return []
        cleaned = re.sub(r"[^a-zA-Z0-9_\s]", " ", text.lower())
        tokens = [t.strip() for t in cleaned.split() if len(t.strip()) > 1]
        return tokens

    def _build_index(self):
        """Indexes all workflows into vector space."""
        workflows = self.registry.list_all()
        if not workflows:
            return

        corpus_tokens: Dict[str, List[str]] = {}
        all_terms = set()

        for wf in workflows:
            # Aggregate semantic fields of the workflow, weighting primary intent fields (name, trigger, decision)
            primary_intent_text = f"{wf.name} {wf.trigger} {wf.decision} " * 2
            combined_text = (
                f"{wf.id} {primary_intent_text} {wf.output} "
                f"{' '.join(wf.inputs)} "
                f"{' '.join(wf.steps)} "
                f"{' '.join(wf.tools)}"
            )
            tokens = self._tokenize(combined_text)
            corpus_tokens[wf.id] = tokens
            all_terms.update(tokens)

        # Compute IDF
        total_docs = len(workflows)
        self._idf = {}
        for term in all_terms:
            doc_freq = sum(1 for tokens in corpus_tokens.values() if term in tokens)
            self._idf[term] = math.log((total_docs + 1) / (doc_freq + 1)) + 1.0

        # Compute TF-IDF vectors
        self._vector_index = {}
        self._doc_lengths = {}
        for wf_id, tokens in corpus_tokens.items():
            tf: Dict[str, float] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0.0) + 1.0

            # TF-IDF weights
            vector: Dict[str, float] = {}
            sq_sum = 0.0
            for t, count in tf.items():
                tfidf = (1.0 + math.log(count)) * self._idf.get(t, 1.0)
                vector[t] = tfidf
                sq_sum += tfidf * tfidf

            length = math.sqrt(sq_sum) if sq_sum > 0 else 1.0
            # Normalize vector
            self._vector_index[wf_id] = {t: val / length for t, val in vector.items()}
            self._doc_lengths[wf_id] = length

        logger.info(f"VectorWorkflowRetriever indexed {len(workflows)} workflows successfully.")

    def search_top_k(self, query: str, k: int = 10) -> List[CandidateWorkflow]:
        """
        Computes cosine similarity between query vector and indexed workflow vectors,
        returning the Top-K candidate workflows (default Top-10 recall) with rank and reciprocal rank.
        """
        if not self._vector_index:
            self._build_index()

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        # Build query TF-IDF vector
        q_tf: Dict[str, float] = {}
        for t in query_tokens:
            q_tf[t] = q_tf.get(t, 0.0) + 1.0

        q_vec: Dict[str, float] = {}
        sq_sum = 0.0
        for t, count in q_tf.items():
            if t in self._idf:
                tfidf = (1.0 + math.log(count)) * self._idf[t]
                q_vec[t] = tfidf
                sq_sum += tfidf * tfidf

        q_length = math.sqrt(sq_sum) if sq_sum > 0 else 1.0
        q_norm = {t: val / q_length for t, val in q_vec.items()}

        # Compute Cosine Similarity against all workflows
        scores: List[Tuple[str, float]] = []
        for wf_id, doc_norm in self._vector_index.items():
            dot_product = sum(weight * doc_norm.get(term, 0.0) for term, weight in q_norm.items())
            if dot_product > 0.0:
                scores.append((wf_id, round(float(dot_product), 4)))

        # Sort descending by score
        scores.sort(key=lambda x: x[1], reverse=True)

        candidates: List[CandidateWorkflow] = []
        for rank, (wf_id, score) in enumerate(scores[:k], start=1):
            wf = self.registry.get(wf_id)
            if wf:
                candidates.append(
                    CandidateWorkflow(
                        workflow_id=wf.id,
                        name=wf.name,
                        trigger=wf.trigger,
                        similarity_score=min(1.0, score),
                        rank=rank,
                        reciprocal_rank=round(1.0 / rank, 4)
                    )
                )

        return candidates

    def compute_mrr(self, target_wf_id: str, candidates: List[CandidateWorkflow]) -> float:
        """
        Calculates the Mean Reciprocal Rank (MRR) for the target workflow
        among the retrieved candidates (1.0 if ranked #1, 0.5 for #2, 0.0 if not recalled).
        """
        for candidate in candidates:
            if candidate.workflow_id.upper() == target_wf_id.upper():
                return candidate.reciprocal_rank
        return 0.0
