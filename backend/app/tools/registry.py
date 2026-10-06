from typing import Any, Callable, Dict, List, Optional
from backend.app.core.logging import get_logger
from backend.app.tools.base import BaseTool, FunctionTool, ToolResult
from backend.app.tools.file_tools import CSVReaderTool, ExcelReaderTool, ColumnNormalizerTool, DataValidatorTool
from backend.app.tools.calc_tools import CalculatorTool
from backend.app.tools.product_tools import TextSimilarityTool, DuplicateProductDetectorTool
from backend.app.tools.order_tools import OrderLookupTool, ShipmentLookupTool
from backend.app.tools.employee_tools import EmployeeRankingTool
from backend.app.tools.llm_tools import LLMGenerateTool
from backend.app.tools.reporting_tools import ReportingTool

logger = get_logger(__name__)

# Alias mapping from Excel tools string to canonical registered tool names
TOOL_NAME_ALIASES: Dict[str, str] = {
    "csv reader": "csv_reader",
    "csv_reader": "csv_reader",
    "excel reader": "excel_reader",
    "excel/csv parser": "csv_reader",
    "excel parser": "excel_reader",
    "calculator": "calculator",
    "data validation": "data_validator",
    "data_validator": "data_validator",
    "data validator": "data_validator",
    "text validation": "data_validator",
    "llm": "llm_generate",
    "llm_generate": "llm_generate",
    "llm generator": "llm_generate",
    "llm/classifier": "llm_generate",
    "order database/api": "order_lookup",
    "order database": "order_lookup",
    "order lookup": "order_lookup",
    "order_lookup": "order_lookup",
    "shipment lookup": "shipment_lookup",
    "shipment_lookup": "shipment_lookup",
    "text similarity": "duplicate_product_detector",
    "text_similarity": "text_similarity",
    "csv/database reader": "csv_reader",
    "product data reader": "csv_reader",
    "employee/task db": "ranking_tool",
    "employee lookup": "ranking_tool",
    "ranking logic": "ranking_tool",
    "ranking_tool": "ranking_tool",
    "reporting": "reporting_tool",
    "reporting_tool": "reporting_tool",
    "reporting tool": "reporting_tool"
}

class ToolRegistry:
    """
    Central repository for registering, retrieving, and discovering workflow tools.
    Supports tool aliasing and automatic resolution of natural names from Excel.
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Registers the standard suite of tools required by the 10 workflows."""
        self.register(CSVReaderTool())
        self.register(ExcelReaderTool())
        self.register(ColumnNormalizerTool())
        self.register(DataValidatorTool())
        self.register(CalculatorTool())
        self.register(TextSimilarityTool())
        self.register(DuplicateProductDetectorTool())
        self.register(OrderLookupTool())
        self.register(ShipmentLookupTool())
        self.register(EmployeeRankingTool())
        self.register(LLMGenerateTool())
        self.register(ReportingTool())

    def register(self, tool: BaseTool) -> None:
        """Registers a BaseTool instance."""
        canonical_name = tool.name.strip().lower()
        self._tools[canonical_name] = tool
        logger.debug(f"Registered tool: '{canonical_name}' ({tool.description})")

    def register_function(self, name: str, description: str, func: Callable[..., Any]) -> None:
        """Helper to register a standalone function as a tool."""
        self.register(FunctionTool(name=name, description=description, func=func))

    def get(self, name: str) -> Optional[BaseTool]:
        """Retrieves a tool by name or alias. Returns None if unresolvable."""
        clean = str(name).strip().lower()
        canonical = TOOL_NAME_ALIASES.get(clean, clean)
        return self._tools.get(canonical)

    def get_or_raise(self, name: str) -> BaseTool:
        """Retrieves a tool by name or raises KeyError."""
        tool = self.get(name)
        if not tool:
            raise KeyError(f"Tool '{name}' is not registered in ToolRegistry. Available tools: {self.list_tools()}")
        return tool

    def exists(self, name: str) -> bool:
        """Checks if a tool name or alias exists."""
        return self.get(name) is not None

    def list_tools(self) -> List[str]:
        """Returns sorted list of all registered canonical tool names."""
        return sorted(self._tools.keys())

# Shared global ToolRegistry singleton
_global_tool_registry = ToolRegistry()

def get_tool_registry() -> ToolRegistry:
    """Returns the shared ToolRegistry instance."""
    return _global_tool_registry
