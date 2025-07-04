from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from . import agent, feedback

app = FastAPI(
    title="Self-Healing AI System",
    description="An API for an AI agent that can self-heal and learn from feedback.",
    version="1.0.0"
)

# --- Pydantic Models for Request/Response Body ---
class AskRequest(BaseModel):
    query: str

class FeedbackRequest(BaseModel):
    query: str
    original_response: str
    feedback: str # "thumbs_up" or "thumbs_down"
    corrected_answer: str | None = None

# --- API Endpoints ---
@app.get("/", summary="Health Check")
def read_root():
    """Health check endpoint to ensure the service is running."""
    return {"status": "ok", "message": "Welcome to the Self-Healing AI API"}

@app.post("/ask", summary="Ask the AI Agent")
def ask_question(request: AskRequest):
    """
    Receives a query, passes it to the agent, and returns the agent's response.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    response = agent.ask_agent(request.query)
    return response

@app.post("/feedback", summary="Provide Feedback")
def give_feedback(request: FeedbackRequest):
    """
    Receives user feedback and logs it. If a correction is provided,
    it's used to patch the agent's memory.
    """
    if request.feedback not in ["thumbs_up", "thumbs_down"]:
        raise HTTPException(status_code=400, detail="Feedback must be 'thumbs_up' or 'thumbs_down'")
        
    feedback.record_feedback(
        query=request.query,
        response=request.original_response,
        feedback_type=request.feedback,
        corrected_answer=request.corrected_answer
    )
    return {"status": "success", "message": "Thank you for your feedback!"}

# To run this app locally:
# uvicorn app.main:app --reload