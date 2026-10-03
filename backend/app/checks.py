import trimesh
import numpy as np

def run_checks(mesh: trimesh.Trimesh, params: dict):
    # Watertight
    is_watertight = mesh.is_watertight
    
    # Volume in cm^3 (mesh.volume is in mm^3)
    volume_cm3 = mesh.volume / 1000.0 if mesh.volume else 0.0
    
    # Filament weight
    petg_density = 1.27 # g/cm3
    # Sockets are thin-walled, assume mostly solid (100% infill for walls)
    grams = volume_cm3 * petg_density
    
    # Cost
    price_per_kg = 4500.0 # Approximate local price for PLA/PETG in Punjab (PKR)
    cost = (grams / 1000.0) * price_per_kg
    
    # Max overhang angle
    normals = mesh.face_normals
    down_faces = normals[normals[:, 2] < 0]
    if len(down_faces) > 0:
        dot = np.clip(-down_faces[:, 2], -1.0, 1.0)
        angles = np.degrees(np.arccos(dot))
        max_overhang = float(np.max(angles))
    else:
        max_overhang = 0.0
        
    return {
        "is_watertight": bool(is_watertight),
        "volume_cm3": round(float(volume_cm3), 2),
        "weight_grams": round(float(grams), 2),
        "cost_estimate": round(float(cost), 2),
        "max_overhang_deg": round(max_overhang, 1),
        "requested_wall_mm": params.get('wall_mm', 3.5)
    }
