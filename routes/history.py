from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from models.db import Generation
from models.response import GenerationResponse
from typing import List, Optional

# from main import get_db
from database import get_db

router = APIRouter()

# @router.get("/history")
# def get_all_history(db: Session = Depends(get_db)):
#     return db.query(Generation).all()


@router.get("/history", response_model=List[GenerationResponse])
def get_all_history(db: Session = Depends(get_db)):
    
    return db.query(Generation).all()

@router.get("/history", response_model=List[GenerationResponse])
def get_all_history(
    skip: int = 0,
    limit: int = 10,
    workflow: Optional[str] = Query(None, description="Filter by workflow name"),
    db: Session = Depends(get_db)
):
    query = db.query(Generation)
    
    if workflow:
        query = query.filter(Generation.workflow_name == workflow)
    
    return query.offset(skip).limit(limit).all()



@router.get("/history/{gen_id}")
def get_history(gen_id: int, db: Session = Depends(get_db)):
    item = db.query(Generation).filter(Generation.id == gen_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Generation not found")
    return item
