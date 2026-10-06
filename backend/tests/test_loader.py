from pathlib import Path
import pytest
import openpyxl
from backend.app.workflow.loader import ExcelWorkflowLoader
from backend.app.workflow.validator import WorkflowValidationError

def test_excel_file_loads_successfully(excel_path: Path):
    """Test 1: Excel file loads successfully."""
    loader = ExcelWorkflowLoader(excel_path)
    workflows = loader.load()
    assert isinstance(workflows, list)
    assert len(workflows) > 0

def test_all_10_workflows_loaded(excel_path: Path):
    """Test 2: All 10 workflows are loaded from the Excel file."""
    loader = ExcelWorkflowLoader(excel_path)
    workflows = loader.load()
    assert len(workflows) == 10
    
    workflow_ids = [w.id for w in workflows]
    expected_ids = [f"WF{i:03d}" for i in range(1, 11)]
    assert sorted(workflow_ids) == sorted(expected_ids)

def test_wf001_and_wf010_content(excel_path: Path):
    """Test 3 & 4: WF001 and WF010 exist and contain structured fields."""
    loader = ExcelWorkflowLoader(excel_path)
    workflows = {w.id: w for w in loader.load()}
    
    # Check WF001
    assert "WF001" in workflows
    wf1 = workflows["WF001"]
    assert wf1.name == "Inventory Restock Check"
    assert "Product inventory CSV" in wf1.inputs
    assert len(wf1.steps) >= 3
    assert "CSV reader" in wf1.tools
    assert "calculator" in wf1.tools
    
    # Check WF010
    assert "WF010" in workflows
    wf10 = workflows["WF010"]
    assert wf10.name == "Workflow Performance Report"
    assert "Workflow execution logs" in wf10.inputs
    assert "reporting" in wf10.tools

def test_loader_handles_missing_file(tmp_path: Path):
    """Test loader raises FileNotFoundError if file is missing."""
    non_existent = tmp_path / "does_not_exist.xlsx"
    loader = ExcelWorkflowLoader(non_existent)
    with pytest.raises(FileNotFoundError):
        loader.load()

def test_loader_handles_corrupted_empty_file(tmp_path: Path):
    """Test loader raises WorkflowValidationError if sheet is empty or missing headers."""
    empty_file = tmp_path / "empty.xlsx"
    wb = openpyxl.Workbook()
    wb.save(empty_file)
    
    loader = ExcelWorkflowLoader(empty_file)
    with pytest.raises(WorkflowValidationError):
        loader.load()
