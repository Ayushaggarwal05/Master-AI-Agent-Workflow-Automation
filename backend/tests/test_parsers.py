from backend.app.utils.parsers import parse_delimited_list, clean_token, clean_step_item

def test_parse_arrow_delimited_steps():
    raw = "Load inventory → compare current stock with minimum threshold → identify low-stock products → calculate reorder quantity → generate restock list."
    result = parse_delimited_list(raw)
    assert len(result) == 5
    assert result[0] == "Load inventory"
    assert result[1] == "compare current stock with minimum threshold"
    assert result[-1] == "generate restock list."

def test_parse_semicolon_delimited():
    raw = "Product inventory CSV; minimum stock threshold"
    result = parse_delimited_list(raw)
    assert len(result) == 2
    assert result[0] == "Product inventory CSV"
    assert result[1] == "minimum stock threshold"

def test_parse_comma_delimited():
    raw = "CSV reader, calculator"
    result = parse_delimited_list(raw)
    assert len(result) == 2
    assert result[0] == "CSV reader"
    assert result[1] == "calculator"

def test_parse_newlines_and_bullets():
    raw = "1. First step\n2. Second step\n• Third step"
    result = parse_delimited_list(raw)
    assert len(result) == 3
    assert result[0] == "First step"
    assert result[1] == "Second step"
    assert result[2] == "Third step"

def test_parse_empty_or_none():
    assert parse_delimited_list(None) == []
    assert parse_delimited_list("") == []
    assert parse_delimited_list("nan") == []
    assert parse_delimited_list("None") == []
