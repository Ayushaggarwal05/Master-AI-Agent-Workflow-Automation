from fastapi import APIRouter
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.workflows import router as workflows_router
from backend.app.api.routes.execution import router as execution_router
from backend.app.api.routes.upload import router as upload_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(workflows_router)
api_router.include_router(execution_router)
api_router.include_router(upload_router)
