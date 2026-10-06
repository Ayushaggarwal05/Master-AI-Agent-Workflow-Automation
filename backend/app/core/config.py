import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env file."""
    
    # Base paths
    APP_DIR: Path = Path(__file__).resolve().parent.parent
    BACKEND_DIR: Path = APP_DIR.parent
    PROJECT_ROOT: Path = BACKEND_DIR.parent
    
    # App Settings
    PROJECT_NAME: str = "AI Agent Workflow Automation"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    HOST: str = Field(default="0.0.0.0", description="Server bind host")
    PORT: int = Field(default=8000, description="Server bind port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Excel Workflow Settings
    WORKFLOW_EXCEL_PATH: str = Field(
        default="data/workflows.xlsx",
        description="Path to the Excel file containing workflow definitions"
    )
    
    # Future Stage 2 AI Configuration (Optional in Stage 1)
    LLM_PROVIDER: Optional[str] = Field(default=None, description="LLM provider (openai, anthropic, etc.)")
    LLM_API_KEY: Optional[str] = Field(default=None, description="LLM API key")
    MODEL_NAME: Optional[str] = Field(default=None, description="LLM Model Name")
    
    model_config = SettingsConfigDict(
        env_file=(
            str(Path(__file__).resolve().parent.parent.parent / ".env"),
            str(Path(__file__).resolve().parent.parent.parent.parent / ".env"),
            ".env"
        ),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def resolved_excel_path(self) -> Path:
        """Resolves the Excel path dynamically relative to CWD, backend dir, or project root."""
        raw_path = Path(self.WORKFLOW_EXCEL_PATH)
        if raw_path.is_absolute() and raw_path.exists():
            return raw_path
            
        candidates = [
            Path.cwd() / raw_path,
            self.PROJECT_ROOT / raw_path,
            self.BACKEND_DIR / raw_path,
            self.PROJECT_ROOT / "data" / "workflows.xlsx",
            self.BACKEND_DIR / "data" / "workflows.xlsx"
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()
                
        # Return candidate from project root by default
        return (self.PROJECT_ROOT / raw_path).resolve()

settings = Settings()
