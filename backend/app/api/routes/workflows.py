from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, status
from backend.app.workflow.models import (
    WorkflowDefinition, 
    WorkflowListResponse, 
    WorkflowDetailResponse,
    WorkflowSummary
)
from backend.app.workflow.registry import get_workflow_registry, WorkflowNotFoundError

router = APIRouter(prefix="/workflows", tags=["Workflows"])

@router.get(
    "",
    response_model=WorkflowListResponse,
    summary="List All Workflows",
    description="Returns all registered AI agent workflows loaded from the Excel source of truth."
)
async def list_workflows():
    registry = get_workflow_registry()
    workflows = registry.list_all()
    return WorkflowListResponse(
        total=len(workflows),
        workflows=workflows
    )

@router.get(
    "/summaries",
    response_model=List[WorkflowSummary],
    summary="List Workflow Summaries",
    description="Returns lightweight summaries of all registered workflows."
)
async def list_workflow_summaries():
    registry = get_workflow_registry()
    return registry.get_summaries()

@router.get(
    "/router-metadata",
    response_model=List[Dict[str, Any]],
    summary="Workflow Metadata for AI Router",
    description="Provides compact metadata structures for semantic matching in Stage 2 AI routing."
)
async def get_router_metadata():
    registry = get_workflow_registry()
    return registry.get_metadata_for_router()

@router.get(
    "/{workflow_id}",
    response_model=WorkflowDetailResponse,
    summary="Get Workflow by ID",
    description="Retrieves a single workflow definition by its unique identifier (e.g. WF001)."
)
async def get_workflow(workflow_id: str):
    registry = get_workflow_registry()
    workflow = registry.get(workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow with ID '{workflow_id.upper()}' not found in registry."
        )
    return WorkflowDetailResponse(workflow=workflow)
