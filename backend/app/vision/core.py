import cv2
import numpy as np
import math
from typing import Tuple, List, Optional
import rembg
from app.geometry.core import CrossSection

def manual_scale(px_distance: float, real_mm: float) -> float:
    return real_mm / px_distance

def calibrate(image: np.ndarray, marker_mm: float) -> float:
    """
    Finds ArUco marker (DICT_4X4_50) and returns mm_per_px.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    
    # Handle OpenCV API differences
    if hasattr(cv2.aruco, 'ArucoDetector'):
        detector = cv2.aruco.ArucoDetector(dictionary, parameters)
        corners, ids, rejected = detector.detectMarkers(gray)
    else:
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)
        
    if ids is None or len(corners) == 0:
        raise ValueError("No ArUco marker found in image.")
        
    # Take the first marker found
    c = corners[0][0]
    # Calculate lengths of the 4 sides
    s1 = np.linalg.norm(c[0] - c[1])
    s2 = np.linalg.norm(c[1] - c[2])
    s3 = np.linalg.norm(c[2] - c[3])
    s4 = np.linalg.norm(c[3] - c[0])
    avg_px = (s1 + s2 + s3 + s4) / 4.0
    
    return float(marker_mm / avg_px)

def segment_limb(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Segment the limb and return (binary_mask, debug_overlay).
    """
    mask = rembg.remove(image, only_mask=True)
    
    # Keep largest connected component
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
    if num_labels > 1:
        largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        mask = (labels == largest_label).astype(np.uint8) * 255
        
    # Create debug overlay
    overlay = image.copy()
    overlay[mask == 0] = overlay[mask == 0] // 2  # darken background
    
    return mask, overlay

def extract_profile(mask: np.ndarray, mm_per_px: float, axis: str = "vertical", n_levels: int = 12) -> List[Tuple[float, float]]:
    """
    Align mask using PCA and measure extent at n_levels.
    Returns [(z_mm, width_mm)] from distal (z=0) to proximal.
    Assumptions: elliptical cross-sections, camera roughly perpendicular, plain background.
    """
    y, x = np.nonzero(mask)
    if len(x) == 0:
        raise ValueError("Empty mask.")
        
    coords = np.column_stack((x, y))
    mean = np.mean(coords, axis=0)
    cov = np.cov(coords, rowvar=False)
    evals, evecs = np.linalg.eigh(cov)
    
    # Principal axis
    sort_indices = np.argsort(evals)[::-1]
    e1 = evecs[:, sort_indices[0]] # largest eigenvector
    
    # Calculate angle to rotate to vertical
    angle = np.arctan2(e1[1], e1[0])
    angle_deg = np.degrees(angle)
    
    # We want it vertical
    target_angle = 90.0
    rotation_diff = target_angle - angle_deg
    
    center = (int(mean[0]), int(mean[1]))
    h, w = mask.shape
    M = cv2.getRotationMatrix2D(center, rotation_diff, 1.0)
    rotated_mask = cv2.warpAffine(mask, M, (w, h), flags=cv2.INTER_NEAREST)
    
    y_rot, x_rot = np.nonzero(rotated_mask)
    if len(y_rot) == 0:
        raise ValueError("Mask empty after rotation.")
        
    y_min, y_max = y_rot.min(), y_rot.max()
    
    profile = []
    # OpenCV y goes down, so y_max is bottom/distal. We step from y_max to y_min
    y_steps = np.linspace(y_max, y_min, n_levels)
    for y_val in y_steps:
        y_int = int(round(y_val))
        row = rotated_mask[y_int, :]
        x_indices = np.nonzero(row)[0]
        if len(x_indices) > 0:
            width_px = x_indices[-1] - x_indices[0]
        else:
            width_px = 0
            
        z_px = y_max - y_val # distance from distal end
        z_mm = float(z_px * mm_per_px)
        width_mm = float(width_px * mm_per_px)
        profile.append((z_mm, width_mm))
        
    return profile

def combine_views(front_profile: List[Tuple[float, float]], side_profile: List[Tuple[float, float]]) -> List[CrossSection]:
    """
    Merge front (width) and side (depth) profiles into 3D sections.
    Resamples both to the same Z levels.
    """
    sections = []
    side_zs = [p[0] for p in side_profile]
    side_ds = [p[1] for p in side_profile]
    
    for z_mm, width_mm in front_profile:
        # Interpolate depth at this z_mm
        depth_mm = float(np.interp(z_mm, side_zs, side_ds))
        sections.append(CrossSection(z_mm=z_mm, width_mm=width_mm, depth_mm=depth_mm))
        
    return sections

def manual_override_circumferences(circumferences_mm: List[float], length_mm: float) -> List[CrossSection]:
    """
    Given circumferences at equal levels, convert to ellipse sections.
    Assumption: depth/width ratio is 0.85 (elliptical cross sections).
    """
    sections = []
    n = len(circumferences_mm)
    ratio = 0.85
    for i, c in enumerate(circumferences_mm):
        z_mm = (i / max(1, (n - 1))) * length_mm
        # C approx = pi * (w + d) / 2
        # d = ratio * w
        w = (2 * c) / (math.pi * (1 + ratio))
        d = w * ratio
        sections.append(CrossSection(z_mm=float(z_mm), width_mm=float(w), depth_mm=float(d)))
    return sections
