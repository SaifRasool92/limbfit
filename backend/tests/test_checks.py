import pytest
from app.checks import run_checks
import trimesh
import numpy as np

def test_run_checks_watertight():
    # Create a simple box mesh which is watertight
    mesh = trimesh.creation.box()
    params = {"wall_mm": 4.0}
    
    results = run_checks(mesh, params)
    
    assert results["is_watertight"] is True
    assert results["volume_cm3"] > 0
    assert results["weight_grams"] > 0
    assert results["cost_estimate"] > 0
    assert results["requested_wall_mm"] == 4.0

def test_run_checks_overhang():
    # Create a box, max overhang should be 90 or 0 depending on orientation
    mesh = trimesh.creation.box()
    params = {"wall_mm": 3.5}
    results = run_checks(mesh, params)
    assert "max_overhang_deg" in results
