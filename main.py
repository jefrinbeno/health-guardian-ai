from fastapi import FastAPI
from pydantic import BaseModel
from src.assistant import HealthGuardian

# 1. Initialize the FastAPI server
app = FastAPI(title="Health Guardian Command Center")

# 2. Initialize the AI Brain 
assistant = HealthGuardian()

# Data model for the incoming Streamlit request
class ContextRequest(BaseModel):
    is_working: bool

@app.get("/")
def read_root():
    """Root endpoint for basic backend health checks."""
    return {"message": "Health Guardian AI Backend is Live."}

@app.post("/api/analyze")
def analyze_health(request: ContextRequest):
    """The standard reactive health check (Minority Report 3D Graph)."""
    result = assistant.analyze_wellbeing({"is_working": request.is_working})
    return {"status": "success", "analysis": result}

@app.post("/api/predict")
def predict_schedule():
    """Triggers the predictive Calendar Armor."""
    # The fix: successfully calling the assistant variable defined on line 9!
    result = assistant.run_predictive_scan() 
    return {"status": "success", "analysis": result}