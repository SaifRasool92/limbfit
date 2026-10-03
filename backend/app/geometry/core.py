import trimesh
import numpy as np
from pydantic import BaseModel
from typing import List
import os

class CrossSection(BaseModel):
    z_mm: float
    width_mm: float
    depth_mm: float

class SocketParams(BaseModel):
    """
    PLACEHOLDER - validate with a prosthetist
    """
    relief_pct: float = 2.0
    wall_mm: float = 3.5
    trim_height_mm: float = 10.0
    vent_count: int = 6
    vent_diameter_mm: float = 4.0
    hole_diameter_mm: float = 6.5

def build_limb_mesh(sections: List[CrossSection]) -> trimesh.Trimesh:
    """
    Loft ellipses (64 points each), cap ends, ensure watertight.
    """
    sections = sorted(sections, key=lambda s: s.z_mm)
    n_theta = 64
    theta = np.linspace(0, 2 * np.pi, n_theta, endpoint=False)
    
    vertices = []
    for sec in sections:
        x = (sec.width_mm / 2) * np.cos(theta)
        y = (sec.depth_mm / 2) * np.sin(theta)
        z = np.full(n_theta, sec.z_mm)
        pts = np.column_stack([x, y, z])
        vertices.extend(pts)
        
    vertices = np.array(vertices)
    
    faces = []
    n_sections = len(sections)
    for i in range(n_sections - 1):
        for j in range(n_theta):
            next_j = (j + 1) % n_theta
            p1 = i * n_theta + j
            p2 = i * n_theta + next_j
            p3 = (i + 1) * n_theta + j
            p4 = (i + 1) * n_theta + next_j
            
            faces.append([p1, p2, p3])
            faces.append([p2, p4, p3])
            
    # Bottom cap
    bottom_center_idx = len(vertices)
    bottom_z = sections[0].z_mm
    vertices = np.vstack([vertices, [0, 0, bottom_z]])
    for j in range(n_theta):
        next_j = (j + 1) % n_theta
        faces.append([j, bottom_center_idx, next_j])
        
    # Top cap
    top_center_idx = len(vertices)
    top_z = sections[-1].z_mm
    vertices = np.vstack([vertices, [0, 0, top_z]])
    top_start = (n_sections - 1) * n_theta
    for j in range(n_theta):
        next_j = (j + 1) % n_theta
        faces.append([top_start + j, top_start + next_j, top_center_idx])
        
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh.fix_normals()
    return mesh

def build_socket(limb_mesh: trimesh.Trimesh, params: SocketParams) -> trimesh.Trimesh:
    inner_mesh = limb_mesh.copy()
    scale_xy = 1.0 - (params.relief_pct / 100.0)
    inner_mesh.vertices[:, 0] *= scale_xy
    inner_mesh.vertices[:, 1] *= scale_xy
    
    outer_mesh = inner_mesh.copy()
    # Move vertices along their normals by wall_mm
    outer_mesh.vertices += outer_mesh.vertex_normals * params.wall_mm
    
    try:
        import manifold3d
        # Use manifold3d directly for robust CSG booleans
        m_inner = manifold3d.Manifold(inner_mesh.vertices, inner_mesh.faces)
        m_outer = manifold3d.Manifold(outer_mesh.vertices, outer_mesh.faces)
        m_socket = m_outer - m_inner
        
        # Trim top
        z_max = outer_mesh.vertices[:, 2].max()
        cut_z = z_max - params.trim_height_mm
        box = trimesh.creation.box(extents=[1000, 1000, 200])
        box.apply_translation([0, 0, cut_z + 100])
        m_box = manifold3d.Manifold(box.vertices, box.faces)
        m_socket = m_socket - m_box
        
        # Distal mount plate
        z_min = inner_mesh.vertices[:, 2].min()
        plate = trimesh.creation.box(extents=[50, 50, params.wall_mm])
        plate.apply_translation([0, 0, z_min - (params.wall_mm / 2)])
        m_plate = manifold3d.Manifold(plate.vertices, plate.faces)
        m_socket = m_socket + m_plate
        
        # Bolt hole
        hole = trimesh.creation.cylinder(radius=params.hole_diameter_mm / 2, height=50)
        hole.apply_translation([0, 0, z_min])
        m_hole = manifold3d.Manifold(hole.vertices, hole.faces)
        m_socket = m_socket - m_hole
        
        mesh_data = m_socket.to_mesh()
        socket_mesh = trimesh.Trimesh(vertices=mesh_data.vert_properties, faces=mesh_data.tri_verts)
        return socket_mesh
    except Exception as e:
        print("Manifold API failed, falling back to trimesh booleans:", e)
        # fallback using trimesh booleans which might use manifold3d engine anyway
        socket_mesh = outer_mesh.difference(inner_mesh)
        return socket_mesh

def export_stl(mesh: trimesh.Trimesh, path: str):
    mesh.export(path)

def export_glb(mesh: trimesh.Trimesh, path: str):
    mesh.export(path)
