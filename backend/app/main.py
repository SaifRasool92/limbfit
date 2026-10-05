from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List
import time
import os
import uuid
import cv2
import numpy as np

from app.vision.core import calibrate, segment_limb, extract_profile, combine_views, manual_override_circumferences
from app.geometry.core import build_limb_mesh, build_socket, export_stl, export_glb, SocketParams, CrossSection
from app.checks import run_checks
from app.marker_pdf import generate_aruco_marker_pdf
from app.rag import explain

app = FastAPI(
    title="LimbFit AI Backend",
    description="Backend for LimbFit AI parametric socket generator and RAG.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"], # adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/outputs", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

def _process_image_view(img_bytes: bytes, marker_mm: float) -> tuple:
    t0 = time.time()
    nparr = np.frombuffer(img_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    t1 = time.time()
    mm_per_px = calibrate(image, marker_mm)
    
    t2 = time.time()
    mask, overlay = segment_limb(image)
    
    t3 = time.time()
    profile = extract_profile(mask, mm_per_px)
    
    t4 = time.time()
    timings = {
        "decode": t1 - t0,
        "calibrate": t2 - t1,
        "segment": t3 - t2,
        "extract": t4 - t3
    }
    return profile, overlay, timings

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/marker")
def get_marker(size_mm: float = Query(50.0, ge=20.0, le=200.0)):
    """Generate and return a printable A4 PDF with an ArUco marker at the requested size."""
    try:
        pdf_bytes = generate_aruco_marker_pdf(size_mm)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=aruco_marker_{int(size_mm)}mm.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze(
    front_image: UploadFile = File(...),
    side_image: UploadFile = File(...),
    marker_mm: float = Form(50.0)
):
    try:
        t_start = time.time()
        
        front_bytes = await front_image.read()
        side_bytes = await side_image.read()
        
        front_profile, front_overlay, front_times = _process_image_view(front_bytes, marker_mm)
        side_profile, side_overlay, side_times = _process_image_view(side_bytes, marker_mm)
        
        t_vision = time.time()
        
        sections = combine_views(front_profile, side_profile)
        
        t_combine = time.time()
        
        limb = build_limb_mesh(sections)
        params = SocketParams()
        socket = build_socket(limb, params)
        
        t_geometry = time.time()
        
        run_id = str(uuid.uuid4())[:8]
        stl_name = f"socket_{run_id}.stl"
        glb_name = f"socket_{run_id}.glb"
        front_overlay_name = f"front_overlay_{run_id}.jpg"
        
        export_stl(socket, f"static/outputs/{stl_name}")
        export_glb(socket, f"static/outputs/{glb_name}")
        cv2.imwrite(f"static/outputs/{front_overlay_name}", front_overlay)
        
        t_export = time.time()
        
        checks = run_checks(socket, params.model_dump())
        
        return {
            "sections": [s.model_dump() for s in sections],
            "socket_glb_url": f"/static/outputs/{glb_name}",
            "socket_stl_url": f"/static/outputs/{stl_name}",
            "debug_overlay_urls": [f"/static/outputs/{front_overlay_name}"],
            "checks": checks,
            "timings_ms": {
                "vision": (t_vision - t_start) * 1000,
                "geometry": (t_geometry - t_combine) * 1000,
                "total": (t_export - t_start) * 1000
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class ManualAnalyzeRequest(BaseModel):
    circumferences_mm: List[float]
    length_mm: float

@app.post("/api/analyze_manual")
def analyze_manual(req: ManualAnalyzeRequest):
    t_start = time.time()
    
    sections = manual_override_circumferences(req.circumferences_mm, req.length_mm)
    limb = build_limb_mesh(sections)
    params = SocketParams()
    socket = build_socket(limb, params)
    
    run_id = str(uuid.uuid4())[:8]
    stl_name = f"socket_{run_id}.stl"
    glb_name = f"socket_{run_id}.glb"
    
    export_stl(socket, f"static/outputs/{stl_name}")
    export_glb(socket, f"static/outputs/{glb_name}")
    
    checks = run_checks(socket, params.model_dump())
    
    t_end = time.time()
    
    return {
        "sections": [s.model_dump() for s in sections],
        "socket_glb_url": f"/static/outputs/{glb_name}",
        "socket_stl_url": f"/static/outputs/{stl_name}",
        "checks": checks,
        "timings_ms": {
            "geometry": (t_end - t_start) * 1000,
            "total": (t_end - t_start) * 1000
        }
    }

class RegenerateRequest(BaseModel):
    sections: List[CrossSection]
    params: SocketParams

@app.post("/api/regenerate")
def regenerate(req: RegenerateRequest):
    t_start = time.time()
    
    limb = build_limb_mesh(req.sections)
    socket = build_socket(limb, req.params)
    
    run_id = str(uuid.uuid4())[:8]
    stl_name = f"socket_{run_id}.stl"
    glb_name = f"socket_{run_id}.glb"
    
    export_stl(socket, f"static/outputs/{stl_name}")
    export_glb(socket, f"static/outputs/{glb_name}")
    
    checks = run_checks(socket, req.params.model_dump())
    
    t_end = time.time()
    
    return {
        "socket_glb_url": f"/static/outputs/{glb_name}",
        "socket_stl_url": f"/static/outputs/{stl_name}",
        "checks": checks,
        "timings_ms": {
            "geometry": (t_end - t_start) * 1000
        }
    }

class ExplainRequest(BaseModel):
    measurements: dict
    params: dict
    checks: dict
    use_rag: bool = True

@app.post("/api/explain")
def explain_endpoint(req: ExplainRequest):
    """
    [RAG IMPLEMENTATION]
    Executes the Retrieval-Augmented Generation (RAG) pipeline to provide
    context-aware clinical rationale and printing guides.
    """
    try:
        explanation = explain(req.measurements, req.params, req.checks, use_rag=req.use_rag)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

