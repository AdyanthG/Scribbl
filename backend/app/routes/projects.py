from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
import uuid
import os
import shutil
from app.services.project_orchestrator import ProjectOrchestrator

router = APIRouter()
orchestrator = ProjectOrchestrator()

# In-memory status store (replace with Redis/DB in prod)
project_status = {}

async def run_pipeline_task(pdf_path: str, project_id: str):
    try:
        async def update_step(step):
            project_status[project_id] = {"status": "processing", "step": step}

        # Run the pipeline
        final_url = await orchestrator.process_project(pdf_path, project_id, update_step)
        
        project_status[project_id] = {
            "status": "completed", 
            "video_url": final_url
        }
    except Exception as e:
        project_status[project_id] = {
            "status": "failed", 
            "error": str(e)
        }
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
        
    # Initialize status
    project_status[project_id] = {"status": "queued"}
    
    # Start background task
    background_tasks.add_task(run_pipeline_task, tmp_path, project_id)
    
    return {"project_id": project_id, "status": "queued"}

@router.get("/list")
def list_projects(ids: str = None):
    """
    List projects. 
    If 'ids' param is provided (comma-separated), return only those projects.
    Otherwise, return all (admin view).
    """
    all_projects = [
        {"id": k, **v} 
        for k, v in project_status.items()
    ]
    
    if ids:
        id_list = ids.split(",")
        return [p for p in all_projects if p["id"] in id_list]
        
    return all_projects

@router.get("/{project_id}/status")
def get_status(project_id: str):
    status = project_status.get(project_id)
    if not status:
        raise HTTPException(status_code=404, detail="Project not found")
    return status
