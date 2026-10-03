import argparse
import math
from app.geometry.core import CrossSection, SocketParams, build_limb_mesh, build_socket, export_stl, export_glb

def main():
    parser = argparse.ArgumentParser(description="LimbFit AI Synthetic Socket Generator")
    parser.add_argument("--arm-circumference", type=float, default=220.0, help="Max arm circumference in mm")
    parser.add_argument("--length", type=float, default=250.0, help="Arm length in mm")
    args = parser.parse_args()
    
    sections = []
    n_levels = 12
    for i in range(n_levels):
        z = (i / (n_levels - 1)) * args.length
        # Taper it down slightly towards distal (z=0)
        taper = 0.6 + 0.4 * (z / args.length)
        c = args.arm_circumference * taper
        w = c / math.pi
        d = w * 0.85
        sections.append(CrossSection(z_mm=z, width_mm=w, depth_mm=d))
        
    print("Building limb mesh...")
    limb = build_limb_mesh(sections)
    print("Building socket...")
    params = SocketParams()
    socket = build_socket(limb, params)
    print("Exporting...")
    export_stl(socket, "out.stl")
    export_glb(socket, "out.glb")
    print("Done! Wrote out.stl and out.glb")

if __name__ == "__main__":
    main()
