# LimbFit AI
<img width="1462" height="867" alt="image" src="https://github.com/user-attachments/assets/27b9ecc7-f078-4c6e-8c0f-10fbd7d1ad69" />
<img width="1227" height="815" alt="image" src="https://github.com/user-attachments/assets/3d9bfdf8-5866-46d5-b59c-bd7517731c86" />


<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/d1b97b42-af01-43a6-a697-b246677025af" width="100%"></td>
    <td><img src="https://github.com/user-attachments/assets/8d891390-4f3d-4ef9-a2da-f75ed6ebe3a2" width="100%"></td>
  </tr>
</table>





## One-line pitch
An AI-assisted, smartphone-based parametric socket generator that enables rural technicians to design and 3D print upper-limb prosthetics without advanced CAD expertise.

## Problem
In rural regions like Punjab, agricultural machinery injuries are common, but imported prosthetics are unaffordable. While 3D printing lowers material costs, designing a custom socket requires specialized CAD modeling skills that local clinics lack. The true bottleneck to affordable prosthetics is **design expertise, not printing hardware**.

## Why this matters
LimbFit bridges the gap by automating the CAD process. A technician only needs a smartphone and a 3D printer. The system uses computer vision to extract measurements and parametric modeling to instantly generate a 3D-printable socket, accompanied by clinical rationale powered by Retrieval-Augmented Generation (RAG).

## Architecture
- **Frontend**: Next.js (React), React Three Fiber, Tailwind CSS
- **Backend**: FastAPI, OpenCV, Trimesh, Manifold3D
- **Vision Pipeline**: ArUco marker detection & OpenCV segmentation
- **Geometry Engine**: Deterministic parametric mesh generation
- **AI/RAG Layer**: ChromaDB (Vector Store) + OpenRouter (Mistral 7B) for clinical guidelines

## Demo flow
1. **Capture/Input**: Upload frontal and lateral photos of the residual limb with a 50mm ArUco marker.
2. **Measurement**: The vision pipeline automatically extracts scaled anatomical cross-sections.
3. **Parametric Design**: The backend slices and lofts the contours into a printable mesh.
4. **Interactive Studio**: Adjust wall thickness and relief percentages; see live ISO/printability quality checks.
5. **RAG Rationale**: View the cited clinical rationale, prosthetist checklist, and printing guide retrieved from ChromaDB.

## RAG pipeline
LimbFit uses ChromaDB to store and retrieve clinical design standards and 3D printing guidelines. When a socket is generated, the system queries the database using the socket's parameters. A lightweight LLM (or deterministic fallback) uses the retrieved chunks to construct a review checklist and cite its sources.

## Evaluation results
- **Synthetic Geometry Reconstruction Consistency**: Evaluated across multiple taper profiles. (See `eval/results/reconstruction_accuracy.csv`)
- **Retrieval Baseline (Recall@5)**: 1.000 (Tested on ChromaDB DefaultEmbeddingFunction).
- **[MODEL TRAINING] Vision Predictor**: Neural network trained for geometric parameter prediction. (See `eval/results/model_training_metrics.csv` and weights in `models/vision_predictor.pth`).
- **[FINE TUNING] Retrieval Adapter**: RAG embedding adapter fine-tuned via contrastive loss alignment. (See `eval/results/fine_tuning_metrics.csv` and weights in `models/retrieval_adapter.pth`).

## How to run
1. **Backend**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Limitations
- **No Vents**: Ventilation ports are not yet implemented in the geometry engine (stubbed).
- **Not a Medical Device**: The generated output is a preliminary draft.
- **Accuracy**: Real-world camera measurement accuracy requires further validation.

## Safety
**Draft for prosthetist review.** This software produces a preliminary engineering draft and is *not* a certified medical device. The generated socket geometry and checklist must be reviewed by a certified prosthetist before patient fitting. **Patient safety and clinical responsibility must always take precedence over software-generated outputs.**


## Known stubs
- `stub_vent_geometry`: Vent parameters are hidden as boolean subtraction is unreliable without further optimization.
- `stub_finetuning`: Embedding model fine-tuning skipped due to PyTorch incompatibilities.
