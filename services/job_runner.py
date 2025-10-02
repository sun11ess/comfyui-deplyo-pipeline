from services.comfy import load_and_update_workflow, send_to_comfyui, wait_for_result
from models.db import Job, JobStatusEnum, Generation
from database import SessionLocal
import os

def run_generation(job_id: str, request):
    db = SessionLocal()
    try:
        job = db.query(Job).get(job_id)
        job.status = JobStatusEnum.RUNNING
        db.commit()

        workflow = load_and_update_workflow(
            "workflows/juggernautXL.json",
            request.prompt,
            request.negative_prompt
        )

        response = send_to_comfyui(workflow)
        prompt_id = response.get("prompt_id")

        b64_image, filepath, filename_local = wait_for_result(prompt_id)

        # Save generation to DB
        gen = Generation(
            workflow_name="juggernautXL",
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            file_path=filepath
        )
        db.add(gen)
        db.commit()
        db.refresh(gen)

        # Update job with success
        job.status = JobStatusEnum.COMPLETED
        job.result_id = gen.id
        db.commit()

    except Exception as e:
        job.status = JobStatusEnum.FAILED
        job.error = str(e)
        db.commit()
    finally:
        db.close()
