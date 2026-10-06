import pytest
from backend.app.services.vector_retriever import VectorWorkflowRetriever
from backend.app.workflow.registry import get_workflow_registry

def test_vector_workflow_retriever_indexing_and_search():
    registry = get_workflow_registry()
    retriever = VectorWorkflowRetriever(registry)
    
    # Query 1: Inventory Restocking
    results = retriever.search_top_k("Which products are low on inventory and need to be restocked?", k=3)
    assert len(results) > 0
    assert results[0].workflow_id == "WF001"
    assert results[0].similarity_score > 0.0
    assert results[0].rank == 1
    assert results[0].reciprocal_rank == 1.0

    # Test MRR computation
    mrr = retriever.compute_mrr("WF001", results)
    assert mrr == 1.0

def test_vector_workflow_retriever_order_lookup():
    registry = get_workflow_registry()
    retriever = VectorWorkflowRetriever(registry)
    
    # Query 2: Order status tracking
    results = retriever.search_top_k("Track the status of order ORD-9021 shipment", k=3)
    assert len(results) > 0
    wf_ids = [r.workflow_id for r in results]
    assert "WF005" in wf_ids
    mrr = retriever.compute_mrr("WF005", results)
    assert mrr > 0.0

def test_vector_workflow_retriever_task_assignment():
    registry = get_workflow_registry()
    retriever = VectorWorkflowRetriever(registry)
    
    # Query 3: Employee task assignment
    results = retriever.search_top_k("Assign an engineer to develop python data pipeline", k=3)
    assert len(results) > 0
    wf_ids = [r.workflow_id for r in results]
    assert "WF009" in wf_ids
    mrr = retriever.compute_mrr("WF009", results)
    assert mrr > 0.0
