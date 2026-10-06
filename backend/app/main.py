import sys
from pathlib import Path

# Automatically ensure project root and backend directory are in sys.path
_project_root = str(Path(__file__).resolve().parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging, get_logger
from backend.app.workflow.registry import get_workflow_registry, WorkflowNotFoundError
from backend.app.workflow.validator import WorkflowValidationError
from backend.app.api.routes import api_router

logger = get_logger("webvory.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup configuration, logging initialization, and Excel workflow loading.
    """
    # 1. Setup structured logging
    setup_logging(settings.LOG_LEVEL)
    logger.info(f"Starting {settings.PROJECT_NAME} (v{settings.PROJECT_VERSION}) in {settings.ENVIRONMENT} mode")
    
    # 2. Resolve Excel workflow source of truth
    excel_path = settings.resolved_excel_path
    logger.info(f"Resolving workflow definitions from Excel: {excel_path}")

    # 3. Load workflows into registry
    try:
        registry = get_workflow_registry()
        count = registry.load_from_excel(excel_path)
        logger.info(f"Successfully loaded and registered {count} workflows into registry")
    except Exception as e:
        logger.error(f"CRITICAL: Failed to load workflows on startup: {str(e)}", exc_info=True)
        # We allow the app to boot even if Excel fails so health endpoint can report status,
        # but log error clearly.
    
    yield
    
    logger.info("Application shutting down cleanly.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Backend API foundation for AI Agent Workflow Automation, driven by Excel as the single source of truth.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Enable CORS for React/Vite frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handlers
@app.exception_handler(WorkflowNotFoundError)
async def workflow_not_found_handler(request: Request, exc: WorkflowNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "WorkflowNotFoundError",
            "message": str(exc),
            "workflow_id": exc.workflow_id
        }
    )

@app.exception_handler(WorkflowValidationError)
async def workflow_validation_handler(request: Request, exc: WorkflowValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "WorkflowValidationError",
            "message": exc.message,
            "details": exc.errors
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred processing your request."
        }
    )

# Include API routes (both at root level and /api/v1 for standard REST clients)
app.include_router(api_router)
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
async def root_index():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "endpoints": {
            "health": "/health",
            "workflows": "/workflows",
            "workflow_detail": "/workflows/{workflow_id}",
            "router_metadata": "/workflows/router-metadata"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
