import pytest
import numpy as np
import cv2
import os
from app.vision.core import calibrate, extract_profile, combine_views, manual_override_circumferences

@pytest.fixture
def synthetic_image():
    # 800x600 white image
    img = np.ones((800, 600, 3), dtype=np.uint8) * 255
    
    # Draw ArUco marker (DICT_4X4_50) ID=0
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker_img = cv2.aruco.generateImageMarker(dictionary, 0, 50)
    img[50:100, 50:100] = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)
    
    # Draw a limb silhouette (ellipse) vertically in the center
    # center (300, 400), axes=(50, 200) -> width=100px
    cv2.ellipse(img, (300, 400), (50, 200), 0, 0, 360, (0, 0, 0), -1)
    
    return img

def test_calibrate(synthetic_image):
    # Marker is exactly 50px wide. Passing 50.0mm means 1px = 1mm
    mm_per_px = calibrate(synthetic_image, 50.0)
    assert abs(mm_per_px - 1.0) < 0.05

def test_extract_profile():
    # Use a direct mask to bypass rembg in CI
    mask = np.zeros((800, 600), dtype=np.uint8)
    cv2.ellipse(mask, (300, 400), (50, 200), 0, 0, 360, 255, -1)
    
    mm_per_px = 1.0
    profile = extract_profile(mask, mm_per_px, n_levels=5)
    
    assert len(profile) == 5
    widths = [p[1] for p in profile]
    # max width should be ~100px = 100mm
    assert abs(max(widths) - 100.0) < 3.0 # within 3% tolerance

def test_combine_views():
    front = [(0.0, 100.0), (50.0, 110.0), (100.0, 120.0)]
    side = [(0.0, 80.0), (60.0, 90.0), (100.0, 100.0)]
    sections = combine_views(front, side)
    
    assert len(sections) == 3
    assert sections[0].width_mm == 100.0
    assert sections[0].depth_mm == 80.0
    # At z=50, depth = 80 + (90-80)*(50/60) = 88.333
    assert abs(sections[1].depth_mm - 88.33) < 0.1

def test_manual_override():
    secs = manual_override_circumferences([200, 220, 240], 100.0)
    assert len(secs) == 3
    assert secs[0].z_mm == 0.0
    assert secs[-1].z_mm == 100.0
    assert secs[0].width_mm > 0
    assert secs[0].depth_mm > 0
