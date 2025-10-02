from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from routes import generate, history, jobs

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Mount the "outputs" folder so files are served at /images/
app.mount("/images", StaticFiles(directory="outputs"), name="images")

# Include routers
app.include_router(generate.router)
app.include_router(history.router)
app.include_router(jobs.router)



@app.get("/")
def root():
    return {"message": "ComfyUI API with DB is running"}
