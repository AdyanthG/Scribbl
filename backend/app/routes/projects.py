from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
import uuid
import os
import shutil
from app.services.project_orchestrator import ProjectOrchestrator

from app.services.storage import StorageManager

router = APIRouter()
orchestrator = ProjectOrchestrator()
storage = StorageManager()

async def run_pipeline_task(pdf_path: str, project_id: str):
    status_path = f"projects/{project_id}/status.json"
    
    try:
        async def update_step(step):
            # Read current to preserve other fields if needed, or just overwrite
            status = {"id": project_id, "status": "processing", "step": step}
            storage.save_json(status_path, status)

        # Run the pipeline
        final_url = await orchestrator.process_project(pdf_path, project_id, update_step)
        
        storage.save_json(status_path, {
            "id": project_id,
            "status": "completed", 
            "video_url": final_url
        })
    except Exception as e:
        storage.save_json(status_path, {
            "id": project_id,
            "status": "failed", 
            "error": str(e)
        })
    finally:
        # Cleanup PDF
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

@router.post("/create")
async def create_project(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    project_id = str(uuid.uuid4())
    
    # Save PDF locally
    tmp_path = f"/tmp/{project_id}.pdf"
    with open(tmp_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    # Initialize status in Storage
    status_path = f"projects/{project_id}/status.json"
    storage.save_json(status_path, {"id": project_id, "status": "queued"})
    
    # Start background task
    background_tasks.add_task(run_pipeline_task, tmp_path, project_id)
    
    return {"project_id": project_id, "status": "queued"}

@router.get("/list")
def list_projects(ids: str = None):
    """
    List projects. 
    If 'ids' param is provided (comma-separated), fetch their status JSONs.
    """
    if not ids:
        return []

    id_list = ids.split(",")
    results = []
    
    # Fetch sequentially for now (or use thread pool if slow)
    # Since it's usually < 10 items, sequential is acceptable for MVP
    # but let's use a simple loop
    for pid in id_list:
        status = storage.get_json(f"projects/{pid}/status.json")
        if status:
            results.append(status)
            
    return results

@router.get("/{project_id}/status")
def get_status(project_id: str):
    status = storage.get_json(f"projects/{project_id}/status.json")
    if not status:
        raise HTTPException(status_code=404, detail="Project not found")
    return status
