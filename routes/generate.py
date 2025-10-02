# from fastapi import APIRouter
# from fastapi.responses import JSONResponse
# from models.request import PromptRequest
# from services.comfy import (
#     load_and_update_workflow,
#     send_to_comfyui,
#     wait_for_result,
#     WORKFLOW_FILE,
# )

# router = APIRouter()

# @router.post("/generate")
# def generate(request: PromptRequest):
#     workflow = load_and_update_workflow(
#         WORKFLOW_FILE,
#         request.prompt,
#         request.negative_prompt
#     )

#     response = send_to_comfyui(workflow)
#     prompt_id = response.get("prompt_id")

#     try:
#         b64_image, filepath = wait_for_result(prompt_id)
#     except TimeoutError as e:
#         return JSONResponse(content={"error": str(e)}, status_code=504)

#     return JSONResponse(content={
#         "prompt_id": prompt_id,
#         "file_path": filepath,
#         "image_base64": b64_image
#     })


# from fastapi import APIRouter, HTTPException, Depends
# from fastapi.responses import JSONResponse
# from sqlalchemy.orm import Session
# from models.request import PromptRequest
# from models.db import Generation
# from services.comfy import load_and_update_workflow, send_to_comfyui, wait_for_result
# # from main import get_db
# from database import get_db

# router = APIRouter()

# @router.post("/generate")
# def generate(request: PromptRequest, db: Session = Depends(get_db)):
#     workflow_name = "juggernautXL"  # fixed for now

#     try:
#         workflow = load_and_update_workflow(
#             "workflows/juggernautXL.json",
#             request.prompt,
#             request.negative_prompt
#         )
#     except FileNotFoundError as e:
#         raise HTTPException(status_code=404, detail=str(e))

#     response = send_to_comfyui(workflow)
#     prompt_id = response.get("prompt_id")

#     try:
#         b64_image, filepath, filename_local = wait_for_result(prompt_id)
#     except TimeoutError as e:
#         return JSONResponse(content={"error": str(e)}, status_code=504)

#     # Save to DB
#     db_item = Generation(
#         workflow_name=workflow_name,
#         prompt=request.prompt,
#         negative_prompt=request.negative_prompt,
#         file_path=filepath
#     )
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)

#     return JSONResponse(content={
#         "id": db_item.id,
#         "workflow": workflow_name,
#         "prompt_id": prompt_id,
#         "file_path": filepath,
#         "image_url": f"/images/{filename_local}",
#         "created_at": db_item.created_at.isoformat()
#     })

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from models.request import PromptRequest
from models.db import Job, JobStatusEnum
from database import get_db
from services.job_runner import run_generation
import uuid

router = APIRouter()

@router.post("/generate")
def generate(request: PromptRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job_id = str(uuid.uuid4())

    # Save job in DB
    job = Job(id=job_id, status=JobStatusEnum.PENDING)
    db.add(job)
    db.commit()
    db.refresh(job)

    # Run in background
    background_tasks.add_task(run_generation, job_id, request)

    return {"job_id": job_id, "status": job.status}
