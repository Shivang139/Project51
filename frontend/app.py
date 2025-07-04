import streamlit as st
import requests

# --- Configuration ---
# Replace with your actual Render API URL after deployment
# For local testing, it's "http://127.0.0.1:8000"
# API_URL = "https://self-healing-agent-api.onrender.com" 
API_URL = "http://127.0.0.1:8000"

# --- UI Layout ---
st.set_page_config(page_title="Self-Healing AI", layout="wide")

st.title("🤖 Self-Healing AI System")
st.markdown("Ask a question and see if the agent can answer. If not, it will try to heal itself!")

# Initialize session state to store conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_response" not in st.session_state:
    st.session_state.last_response = {}

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input and API Interaction ---
query = st.chat_input("What would you like to ask?")

if query:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Display spinner while waiting for a response
    with st.spinner("Agent is thinking..."):
        try:
            response = requests.post(f"{API_URL}/ask", json={"query": query}, timeout=60)
            response.raise_for_status() # Raises an exception for 4XX/5XX errors
            
            data = response.json()
            answer = data.get("answer", "No answer found.")
            st.session_state.last_response = {"query": query, "answer": answer}

            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(answer)
                st.info(f"Confidence: {data.get('confidence', 'N/A'):.2f} | Healing Attempts: {data.get('healing_attempts', 'N/A')}")
            
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to the API: {e}")

# --- Feedback Mechanism ---
if st.session_state.last_response:
    st.write("---")
    st.write("Was this answer helpful?")
    
    col1, col2, col3 = st.columns([1, 1, 8])
    
    with col1:
        if st.button("👍"):
            requests.post(f"{API_URL}/feedback", json={
                "query": st.session_state.last_response["query"],
                "original_response": st.session_state.last_response["answer"],
                "feedback": "thumbs_up"
            })
            st.success("Thanks for the feedback!")
            st.session_state.last_response = {} # Clear after feedback

    with col2:
        if st.button("👎"):
            requests.post(f"{API_URL}/feedback", json={
                "query": st.session_state.last_response["query"],
                "original_response": st.session_state.last_response["answer"],
                "feedback": "thumbs_down"
            })
            st.warning("Thanks for the feedback! It helps the system learn.")
            st.session_state.last_response = {} # Clear after feedback