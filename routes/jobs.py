from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.db import Job, Generation
import os

router = APIRouter()

@router.get("/status/{job_id}")
def check_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job.id, "status": job.status, "error": job.error}

@router.get("/result/{job_id}")
def get_result(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "completed":
        return {"job_id": job.id, "status": job.status}

    gen = db.query(Generation).get(job.result_id)
    return {
        "id": gen.id,
        "workflow": gen.workflow_name,
        "file_path": gen.file_path,
        "image_url": f"/images/{os.path.basename(gen.file_path)}",
        "created_at": gen.created_at.isoformat()
    }
