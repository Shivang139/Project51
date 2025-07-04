from pymongo import MongoClient
import datetime
from . import config

# --- MongoDB Connection ---
try:
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]
    logs_collection = db["interaction_logs"]
    feedback_collection = db["user_feedback"]
    print("✅ Successfully connected to MongoDB.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    # The application can continue without logging, but we should know about it.
    logs_collection = None
    feedback_collection = None


def log_interaction(query: str, response: str, confidence: float, healing_attempts: int, success: bool):
    """Logs a full agent interaction to MongoDB."""
    if logs_collection is None:
        return
        
    log_entry = {
        "query": query,
        "response": response,
        "confidence": confidence,
        "healing_attempts": healing_attempts,
        "success": success,
        "timestamp": datetime.datetime.utcnow()
    }
    logs_collection.insert_one(log_entry)

def record_feedback(query: str, response: str, feedback_type: str, corrected_answer: str = None):
    """
    Records user feedback (thumbs up/down) and potential corrections.
    
    Edge Case Handled: Memory pollution. Good examples (thumbs up with correction)
    are stored for potential use, while bad examples are just logged.
    """
    if feedback_collection is None:
        return

    feedback_entry = {
        "query": query,
        "original_response": response,
        "feedback": feedback_type, # "thumbs_up" or "thumbs_down"
        "corrected_answer": corrected_answer,
        "timestamp": datetime.datetime.utcnow()
    }
    feedback_collection.insert_one(feedback_entry)
    
    # Self-healing agent behavior: Use good feedback to patch memory
    if feedback_type == "thumbs_up" and corrected_answer:
        from .memory import vector_memory # Local import to avoid circular dependency
        # Add the corrected answer to the agent's memory as a "golden" example
        vector_memory.add_memory(f"For a query like '{query}', a good answer is: '{corrected_answer}'")