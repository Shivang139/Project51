import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the app directory to the path to import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app
from app.agent import is_response_unclear

client = TestClient(app)

def test_health_check():
    """Tests if the root endpoint is working."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Welcome to the Self-Healing AI API"}

def test_ask_endpoint():
    """Tests the /ask endpoint with a valid query."""
    response = client.post("/ask", json={"query": "Hello, who are you?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 0

def test_ask_endpoint_empty_query():
    """Tests the /ask endpoint with an empty query."""
    response = client.post("/ask", json={"query": ""})
    assert response.status_code == 400 # Bad Request

def test_feedback_endpoint():
    """Tests the /feedback endpoint."""
    feedback_data = {
        "query": "Test query",
        "original_response": "Test response",
        "feedback": "thumbs_up",
        "corrected_answer": "A better response."
    }
    response = client.post("/feedback", json=feedback_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Thank you for your feedback!"

@pytest.mark.parametrize("response, expected", [
    ("", True),
    ("I don't know.", True),
    ("As an AI, I cannot give personal opinions.", True),
    ("This is a perfectly valid and good response.", False),
    ("Here is the answer you requested.", False)
])
def test_is_response_unclear(response, expected):
    """Tests the failure detection logic."""
    assert is_response_unclear(response) == expected