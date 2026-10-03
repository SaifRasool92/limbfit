import pytest
from app.rag.explainer import explain

def test_explain_fallback():
    measurements = {"circumferences_mm": [200, 210, 220], "total_sections": 3}
    params = {"wall_mm": 4.0, "relief_pct": 2.5}
    checks = {"is_watertight": True}
    
    # Test fallback by disabling rag
    result = explain(measurements, params, checks, use_rag=False)
    
    assert "rationale" in result
    assert "checklist" in result
    assert "print_guide" in result
    
    assert "No source-backed guidance was retrieved" in result["rationale"]
    assert "4.0mm" in result["rationale"]
