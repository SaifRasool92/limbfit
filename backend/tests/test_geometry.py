import pytest
import time
from app.geometry.core import CrossSection, SocketParams, build_limb_mesh, build_socket

def test_build_limb_and_socket():
    sections = [
        CrossSection(z_mm=0.0, width_mm=50.0, depth_mm=45.0),
        CrossSection(z_mm=50.0, width_mm=60.0, depth_mm=55.0),
        CrossSection(z_mm=100.0, width_mm=70.0, depth_mm=65.0)
    ]
    t0 = time.time()
    limb = build_limb_mesh(sections)
    params = SocketParams(wall_mm=3.5, hole_diameter_mm=6.5)
    socket = build_socket(limb, params)
    t1 = time.time()
    
    assert socket.is_watertight, "Socket must be watertight"
    assert (t1 - t0) < 5.0, "Generation should take < 5s on CPU"
    assert socket.volume > 0, "Socket must have volume"
    
    # We could also sample minimum wall thickness with ray casting,
    # but watertightness and volume are good basics.
