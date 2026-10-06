from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    """Encapsulates the standard output of a tool invocation."""
    success: bool = True
    data: Any = None
    message: Optional[str] = None
    error: Optional[str] = None


class BaseTool(ABC):
    """Abstract base class for all reusable workflow tools."""
    name: str
    description: str

    @abstractmethod
    def run(self, **kwargs) -> ToolResult:
        """Executes the tool logic with provided kwargs."""
        pass


class FunctionTool(BaseTool):
    """Wraps a callable function into a standard BaseTool."""

    def __init__(self, name: str, description: str, func: Callable[..., Any]):
        self.name = name
        self.description = description
        self.func = func

    def run(self, **kwargs) -> ToolResult:
        try:
            res = self.func(**kwargs)
            if isinstance(res, ToolResult):
                return res
            return ToolResult(success=True, data=res)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
