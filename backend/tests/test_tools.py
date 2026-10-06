import pytest
from backend.app.tools.registry import get_tool_registry
from backend.app.tools.file_tools import CSVReaderTool, ColumnNormalizerTool, DataValidatorTool
from backend.app.tools.calc_tools import CalculatorTool
from backend.app.tools.product_tools import TextSimilarityTool, DuplicateProductDetectorTool
from backend.app.tools.order_tools import OrderLookupTool, ShipmentLookupTool
from backend.app.tools.employee_tools import EmployeeRankingTool
from backend.app.tools.llm_tools import LLMGenerateTool
from backend.app.tools.reporting_tools import ReportingTool

def test_tool_registry_discovery():
    registry = get_tool_registry()
    tools = registry.list_tools()
    assert "csv_reader" in tools
    assert "calculator" in tools
    assert "duplicate_product_detector" in tools
    assert "order_lookup" in tools
    assert "ranking_tool" in tools
    assert "llm_generate" in tools
    assert "reporting_tool" in tools
    
    # Check alias resolution
    assert registry.get("CSV reader") is not None
    assert registry.get("ranking logic") is not None
    assert registry.get("order database/API") is not None

def test_csv_reader_tool():
    tool = CSVReaderTool()
    res = tool.run(file_path="sample_data/inventory.csv")
    assert res.success is True
    assert len(res.data) > 0
    assert "sku" in res.data[0]

def test_column_normalizer_and_validator():
    norm_tool = ColumnNormalizerTool()
    raw = [
        {"Vendor SKU": "V-101", "Product Title": "Widget A", "Unit Price": "10.0"},
        {"Vendor SKU": "", "Product Title": "Missing SKU Item", "Unit Price": "5.0"},
        {"Vendor SKU": "V-102", "Product Title": "", "Unit Price": "15.0"}
    ]
    norm_res = norm_tool.run(rows=raw)
    assert norm_res.success is True
    assert "sku" in norm_res.data[0]
    assert "name" in norm_res.data[0]

    val_tool = DataValidatorTool()
    val_res = val_tool.run(rows=norm_res.data)
    assert val_res.success is True
    assert val_res.data["valid_count"] == 1
    assert val_res.data["invalid_count"] == 2

def test_calculator_stock_and_price_logic():
    calc = CalculatorTool()
    # Test stock check
    items = [
        {"sku": "P1", "name": "Item 1", "current_stock": 2, "minimum_stock": 10},
        {"sku": "P2", "name": "Item 2", "current_stock": 20, "minimum_stock": 5}
    ]
    stock_res = calc.run(operation="stock_check", items=items)
    assert stock_res.success is True
    assert stock_res.data["restock_required_count"] == 1
    assert stock_res.data["restock_items"][0]["sku"] == "P1"
    assert stock_res.data["restock_items"][0]["suggested_reorder_qty"] == 18.0

    # Test price comparison
    prods = [{"sku": "P1", "name": "Item 1", "unit_price": 100.0}]
    vendors = {"P1": 115.0} # 15% diff (> 10%)
    price_res = calc.run(operation="price_comparison", products=prods, vendor_prices=vendors, threshold_pct=10.0)
    assert price_res.success is True
    assert price_res.data["exception_count"] == 1
    assert price_res.data["exceptions"][0]["difference_pct"] == 15.0

def test_duplicate_product_detector():
    dup_tool = DuplicateProductDetectorTool()
    prods = [
        {"sku": "SKU-A", "name": "Wireless Mouse Black", "attributes": "DPI 4000"},
        {"sku": "SKU-A", "name": "Wireless Mouse Black Edition", "attributes": "DPI 4000"},
        {"sku": "SKU-B", "name": "Gaming Keyboard RGB", "attributes": "Blue Switches"}
    ]
    res = dup_tool.run(products=prods)
    assert res.success is True
    assert res.data["duplicates_found_count"] >= 1
    assert "Exact SKU" in res.data["duplicate_groups"][0]["match_type"]

def test_order_and_shipment_lookup():
    order_tool = OrderLookupTool()
    found_res = order_tool.run(identifier="ORD-9021")
    assert found_res.success is True
    assert found_res.data["order_id"] == "ORD-9021"

    ship_tool = ShipmentLookupTool()
    ship_res = ship_tool.run(order_data=found_res.data)
    assert ship_res.success is True
    assert ship_res.data["carrier"] == "FedEx"
    assert ship_res.data["tracking_number"] == "FDX-99882233"

    not_found = order_tool.run(identifier="INVALID-ORDER")
    assert not_found.success is False
    assert "No order found" in not_found.error

def test_employee_ranking_tool():
    emp_tool = EmployeeRankingTool()
    res = emp_tool.run(
        task_description="Build a high performance Python FastAPI backend and ETL data pipeline",
        required_skills=["Python", "FastAPI", "PostgreSQL", "ETL"],
        priority="High"
    )
    assert res.success is True
    assert res.data["status"] == "ASSIGNED"
    rec = res.data["recommended_employee"]
    assert rec["name"] in ("Sarah Connor", "Elena Rostova", "Alex Chen")

def test_llm_product_content_missing_attributes():
    llm_tool = LLMGenerateTool()
    res = llm_tool.run(
        task_type="product_content",
        product_name="Minimalist Desk Mat",
        category="Office Accessories",
        attributes="Waterproof, Non-slip Base",
        material=None,  # Missing
        color=None      # Missing
    )
    assert res.success is True
    data = res.data
    assert "product_description" in data
    assert "seo_title" in data
    assert "material" in data["explicitly_missing_attributes"]
    assert "color" in data["explicitly_missing_attributes"]

def test_llm_campaign_brief_missing_dates_rejection():
    llm_tool = LLMGenerateTool()
    # Missing dates should fail per workflow decision rule
    fail_res = llm_tool.run(
        task_type="campaign_brief",
        campaign_goal="Increase summer sales by 25%",
        dates=None
    )
    assert fail_res.success is False
    assert "Missing required fields" in fail_res.error

    # With dates provided, should succeed
    ok_res = llm_tool.run(
        task_type="campaign_brief",
        campaign_goal="Increase summer sales by 25%",
        dates="June 1 - July 15"
    )
    assert ok_res.success is True
    assert "campaign_checklist" in ok_res.data

def test_reporting_tool_high_failure_rate():
    rep = ReportingTool()
    logs = [
        {"execution_id": "1", "workflow_id": "WF002", "status": "FAILED", "duration_seconds": 2.0, "error_message": "Price exception"},
        {"execution_id": "2", "workflow_id": "WF002", "status": "FAILED", "duration_seconds": 2.5, "error_message": "Price exception"},
        {"execution_id": "3", "workflow_id": "WF001", "status": "SUCCESS", "duration_seconds": 1.0, "error_message": ""}
    ]
    res = rep.run(logs=logs, fail_threshold_pct=10.0)
    assert res.success is True
    assert res.data["summary_metrics"]["failure_rate_pct"] == 66.67
    assert len(res.data["flagged_workflows"]) == 1
    assert res.data["flagged_workflows"][0]["workflow_id"] == "WF002"
