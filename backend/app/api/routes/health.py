from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.workflow.models import HealthResponse
from backend.app.workflow.registry import get_workflow_registry

router = APIRouter(tags=["Health"])

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    description="Returns the current operational status of the service and workflow registry."
)
async def get_health():
    registry = get_workflow_registry()
    return HealthResponse(
        status="ok",
        version=settings.PROJECT_VERSION,
        environment=settings.ENVIRONMENT,
        workflows_loaded=registry.count(),
        excel_path=str(settings.resolved_excel_path)
    )
