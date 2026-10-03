import io
import struct
import zlib
import math

def generate_aruco_marker_pdf(marker_size_mm: float = 50.0) -> bytes:
    """
    Generate a minimal, printable PDF containing a 50mm ArUco DICT_4X4_50 ID=0 marker
    with crop marks and a caption. Uses only stdlib — no extra deps.
    """
    import cv2
    import numpy as np

    # Generate marker image at 300 DPI
    dpi = 300
    size_px = int((marker_size_mm / 25.4) * dpi)  # mm -> inch -> px

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker_img = cv2.aruco.generateImageMarker(dictionary, 0, size_px)

    # Encode as PNG bytes
    success, buf = cv2.imencode('.png', marker_img)
    if not success:
        raise RuntimeError("Failed to encode marker image.")
    png_bytes = buf.tobytes()

    # A4 page in points (1pt = 1/72 inch)
    PAGE_W = 595.28
    PAGE_H = 841.89
    pt_per_mm = 72.0 / 25.4

    marker_pt = marker_size_mm * pt_per_mm
    # Center the marker
    mx = (PAGE_W - marker_pt) / 2
    my = (PAGE_H - marker_pt) / 2

    # Build PDF manually
    objects = []
    offsets = []

    def add_obj(content: str) -> int:
        n = len(objects) + 1
        objects.append(content)
        return n

    # Object 1: Catalog
    add_obj("<<\n  /Type /Catalog\n  /Pages 2 0 R\n>>")

    # Object 2: Pages
    add_obj("<<\n  /Type /Pages\n  /Kids [3 0 R]\n  /Count 1\n>>")

    # Object 3: Page
    page_content = (
        "<<\n"
        f"  /Type /Page\n"
        f"  /Parent 2 0 R\n"
        f"  /MediaBox [0 0 {PAGE_W:.2f} {PAGE_H:.2f}]\n"
        f"  /Contents 4 0 R\n"
        f"  /Resources <<\n"
        f"    /XObject << /Img 5 0 R >>\n"
        f"    /Font << /F1 6 0 R >>\n"
        f"  >>\n"
        f">>"
    )
    add_obj(page_content)

    # Object 4: Content stream (draw image + caption + crop marks)
    crop = 5  # pt
    stream_lines = [
        f"q",
        f"{marker_pt:.2f} 0 0 {marker_pt:.2f} {mx:.2f} {my:.2f} cm",
        f"/Img Do",
        f"Q",
        # Caption
        f"BT",
        f"/F1 10 Tf",
        f"{mx:.2f} {(my - 16):.2f} Td",
        f"(ArUco DICT_4X4_50  ID=0  Size: {marker_size_mm:.0f}mm  --  LimbFit AI) Tj",
        f"ET",
        # Crop marks
        f"0.5 w",
        # Top-left
        f"{mx - crop:.2f} {my + marker_pt:.2f} m {mx - 1:.2f} {my + marker_pt:.2f} l S",
        f"{mx:.2f} {my + marker_pt + crop:.2f} m {mx:.2f} {my + marker_pt + 1:.2f} l S",
        # Top-right
        f"{mx + marker_pt + 1:.2f} {my + marker_pt:.2f} m {mx + marker_pt + crop:.2f} {my + marker_pt:.2f} l S",
        f"{mx + marker_pt:.2f} {my + marker_pt + crop:.2f} m {mx + marker_pt:.2f} {my + marker_pt + 1:.2f} l S",
        # Bottom-left
        f"{mx - crop:.2f} {my:.2f} m {mx - 1:.2f} {my:.2f} l S",
        f"{mx:.2f} {my - crop:.2f} m {mx:.2f} {my - 1:.2f} l S",
        # Bottom-right
        f"{mx + marker_pt + 1:.2f} {my:.2f} m {mx + marker_pt + crop:.2f} {my:.2f} l S",
        f"{mx + marker_pt:.2f} {my - crop:.2f} m {mx + marker_pt:.2f} {my - 1:.2f} l S",
    ]
    stream = "\n".join(stream_lines).encode()
    stream_obj = (
        f"<<\n  /Length {len(stream)}\n>>\n"
        f"stream\n"
    ).encode() + stream + b"\nendstream"
    objects.append(stream_obj.decode(errors='replace'))  # will be raw-written

    # Object 5: Image XObject
    img_obj_header = (
        f"<<\n"
        f"  /Type /XObject\n"
        f"  /Subtype /Image\n"
        f"  /Width {size_px}\n"
        f"  /Height {size_px}\n"
        f"  /ColorSpace /DeviceGray\n"
        f"  /BitsPerComponent 8\n"
        f"  /Filter /FlateDecode\n"
        f"  /Length {len(png_bytes)}\n"
        f">>\n"
        f"stream\n"
    )

    # Object 6: Font
    add_obj(
        "<<\n"
        "  /Type /Font\n"
        "  /Subtype /Type1\n"
        "  /BaseFont /Helvetica\n"
        ">>"
    )

    # Build raw PDF bytes
    out = io.BytesIO()
    out.write(b"%PDF-1.4\n")
    obj_offsets = []

    for i, obj in enumerate(objects):
        obj_num = i + 1
        obj_offsets.append(out.tell())
        if obj_num == 5:
            # Write image object raw
            out.write(f"{obj_num} 0 obj\n".encode())
            out.write(img_obj_header.encode())
            out.write(png_bytes)
            out.write(b"\nendstream\nendobj\n")
        else:
            out.write(f"{obj_num} 0 obj\n{obj}\nendobj\n".encode())

    # xref
    xref_offset = out.tell()
    out.write(f"xref\n0 {len(objects) + 1}\n".encode())
    out.write(b"0000000000 65535 f \n")
    for off in obj_offsets:
        out.write(f"{off:010d} 00000 n \n".encode())

    out.write(
        f"trailer\n<<\n  /Size {len(objects) + 1}\n  /Root 1 0 R\n>>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode()
    )

    return out.getvalue()
