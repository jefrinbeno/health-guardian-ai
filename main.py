from fastapi import FastAPI
from pydantic import BaseModel
from src.assistant import HealthGuardian

app = FastAPI(title="Health Guardian Command Center")
guardian = HealthGuardian()

# We use this to accept data from our future frontend dashboard
class UserContext(BaseModel):
    is_working: bool

@app.get("/")
def read_root():
    return {"message": "Health Guardian AI Backend is Live."}

@app.post("/api/analyze")
def analyze_status(context: UserContext):
    """
    This endpoint allows the web dashboard to request a health analysis.
    """
    # Call your existing logic!
    result = guardian.analyze_wellbeing({"is_working": context.is_working})
    
    return {
        "status": "success",
        "analysis": result
    }