"""
Phase 7: Reconstruction Accuracy Evaluation Harness

Measures mean circumference error (mm) between the geometry pipeline's output
and synthetic ground-truth cross-sections, as required by the PRD success metrics.

Usage (from limbfit/ root):
    python -m eval.reconstruction_accuracy

Output:
    eval/results/reconstruction_accuracy.csv
"""
import os
import sys
import json
import time
import csv
import math

# Ensure the backend package is importable
_eval_dir  = os.path.dirname(os.path.abspath(__file__))   # limbfit/eval
_repo_root = os.path.dirname(_eval_dir)                   # limbfit
_backend   = os.path.join(_repo_root, "backend")
if _backend not in sys.path:
    sys.path.insert(0, _backend)

from app.geometry.core import CrossSection, SocketParams, build_limb_mesh, build_socket


# ---------------------------------------------------------------------------
# Synthetic Ground Truth Test Cases
# All measurements in millimetres as required by project rules.
# ---------------------------------------------------------------------------
GROUND_TRUTH_CASES = [
    {
        "id": "case_01_short_limb",
        "description": "Short residual limb, 80mm, uniform taper",
        "sections": [
            {"z_mm": 0.0,  "width_mm": 72.0, "depth_mm": 68.0},
            {"z_mm": 20.0, "width_mm": 68.0, "depth_mm": 64.0},
            {"z_mm": 40.0, "width_mm": 62.0, "depth_mm": 58.0},
            {"z_mm": 60.0, "width_mm": 55.0, "depth_mm": 51.0},
            {"z_mm": 80.0, "width_mm": 46.0, "depth_mm": 42.0},
        ]
    },
    {
        "id": "case_02_medium_limb",
        "description": "Medium residual limb, 130mm, irregular taper",
        "sections": [
            {"z_mm": 0.0,  "width_mm": 78.0, "depth_mm": 74.0},
            {"z_mm": 25.0, "width_mm": 74.0, "depth_mm": 70.0},
            {"z_mm": 50.0, "width_mm": 68.0, "depth_mm": 63.0},
            {"z_mm": 75.0, "width_mm": 60.0, "depth_mm": 55.0},
            {"z_mm": 100.0,"width_mm": 52.0, "depth_mm": 47.0},
            {"z_mm": 130.0,"width_mm": 44.0, "depth_mm": 39.0},
        ]
    },
    {
        "id": "case_03_long_limb",
        "description": "Long residual limb, 180mm, near-cylindrical",
        "sections": [
            {"z_mm": 0.0,  "width_mm": 80.0, "depth_mm": 76.0},
            {"z_mm": 40.0, "width_mm": 77.0, "depth_mm": 73.0},
            {"z_mm": 80.0, "width_mm": 73.0, "depth_mm": 69.0},
            {"z_mm": 120.0,"width_mm": 68.0, "depth_mm": 64.0},
            {"z_mm": 160.0,"width_mm": 62.0, "depth_mm": 58.0},
            {"z_mm": 180.0,"width_mm": 57.0, "depth_mm": 53.0},
        ]
    },
    {
        "id": "case_04_manual_input",
        "description": "Manually entered circumferences (simulates manual_override path)",
        "sections": [
            {"z_mm": 0.0,  "width_mm": 65.0, "depth_mm": 61.0},
            {"z_mm": 30.0, "width_mm": 60.0, "depth_mm": 56.0},
            {"z_mm": 60.0, "width_mm": 54.0, "depth_mm": 50.0},
            {"z_mm": 90.0, "width_mm": 48.0, "depth_mm": 44.0},
        ]
    },
]

SOCKET_PARAMS = SocketParams(
    relief_pct=2.0,
    wall_mm=3.5,
    trim_height_mm=10.0,
    vent_count=6,
    vent_diameter_mm=4.0,
    hole_diameter_mm=6.5,
)


def circumference_from_section(section: CrossSection) -> float:
    """Approximate ellipse circumference using Ramanujan's formula (mm)."""
    a = section.width_mm / 2
    b = section.depth_mm / 2
    h = ((a - b) ** 2) / ((a + b) ** 2)
    return math.pi * (a + b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))


def run_case(case: dict) -> dict:
    """
    Build the socket from ground-truth sections, then measure how accurately
    the geometry pipeline reproduces the cross-section circumferences.

    The 'reconstruction error' in this harness measures internal consistency
    (mesh vertices recovered vs. input design intent), since we have no
    real camera image to compare against.
    """
    gt_sections = [CrossSection(**s) for s in case["sections"]]
    gt_circumferences = [circumference_from_section(s) for s in gt_sections]

    t0 = time.perf_counter()
    limb_mesh = build_limb_mesh(gt_sections)
    socket_mesh = build_socket(limb_mesh, SOCKET_PARAMS)
    t_elapsed = (time.perf_counter() - t0) * 1000  # ms

    # Recover cross-section widths from the mesh by slicing at each z_mm
    errors = []
    for i, gt_sec in enumerate(gt_sections):
        z_target = gt_sec.z_mm

        # Find all mesh vertices near this z-level (±2mm tolerance)
        verts = limb_mesh.vertices
        near = verts[abs(verts[:, 2] - z_target) < 2.0]

        if len(near) < 3:
            # Not enough points — skip this section
            continue

        # Recover width and depth from min/max of the slice
        recovered_width = float(near[:, 0].max() - near[:, 0].min())
        recovered_depth = float(near[:, 1].max() - near[:, 1].min())
        recovered_section = CrossSection(
            z_mm=z_target,
            width_mm=recovered_width,
            depth_mm=recovered_depth
        )
        recovered_circ = circumference_from_section(recovered_section)
        gt_circ = gt_circumferences[i]
        errors.append(abs(recovered_circ - gt_circ))

    mean_error = sum(errors) / len(errors) if errors else float("nan")
    max_error  = max(errors)               if errors else float("nan")

    return {
        "case_id":               case["id"],
        "description":           case["description"],
        "n_sections":            len(gt_sections),
        "mean_circ_error_mm":    round(mean_error, 3),
        "max_circ_error_mm":     round(max_error, 3),
        "generation_time_ms":    round(t_elapsed, 1),
        "passes_5s_target":      t_elapsed < 5000,
    }


def main():
    out_dir = os.path.join(_eval_dir, "results")
    os.makedirs(out_dir, exist_ok=True)
    out_csv = os.path.join(out_dir, "reconstruction_accuracy.csv")

    fields = [
        "case_id", "description", "n_sections",
        "mean_circ_error_mm", "max_circ_error_mm",
        "generation_time_ms", "passes_5s_target"
    ]

    print("Phase 7 — Reconstruction Accuracy & Timing Harness")
    print("=" * 55)

    rows = []
    for case in GROUND_TRUTH_CASES:
        print(f"  Running {case['id']}…", end=" ", flush=True)
        row = run_case(case)
        rows.append(row)
        status = "✓" if row["passes_5s_target"] else "✗ SLOW"
        print(f"mean_err={row['mean_circ_error_mm']}mm  time={row['generation_time_ms']}ms  [{status}]")

    # Summary
    mean_errors = [r["mean_circ_error_mm"] for r in rows if not math.isnan(r["mean_circ_error_mm"])]
    times_ms    = [r["generation_time_ms"]  for r in rows]
    all_pass    = all(r["passes_5s_target"] for r in rows)

    print()
    print(f"  Overall mean circumference error : {sum(mean_errors)/len(mean_errors):.3f} mm")
    print(f"  Overall mean generation time     : {sum(times_ms)/len(times_ms):.1f} ms")
    print(f"  All cases pass <5s target        : {all_pass}")

    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n  Results written to {out_csv}")


if __name__ == "__main__":
    main()
