# File: backend/app/agent.py

# --- BEFORE ---
# from langchain_openai import ChatOpenAI
# ...

# --- AFTER ---
from langchain_google_genai import ChatGoogleGenerativeAI # <-- CHANGE THIS IMPORT
from langchain.prompts import PromptTemplate
from . import config, feedback, memory
import time

# --- Agent Configuration ---

# --- BEFORE ---
# llm = ChatOpenAI(
#     model="gpt-4",
#     temperature=0.7,
#     api_key=config.OPENAI_API_KEY
# )
# fallback_llm = ChatOpenAI(
#     model="gpt-3.5-turbo",
#     temperature=0.7,
#     api_key=config.OPENAI_API_KEY
# )

# --- AFTER ---
# Use Gemini 1.5 Flash as the main model. It's fast and powerful.
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    google_api_key=config.GOOGLE_API_KEY
)

# For a fallback, we can use the same model or a slightly different configuration.
# Here we'll just use the same model, as Flash is already very efficient.
fallback_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.9, # Maybe increase temperature for a different kind of response
    google_api_key=config.GOOGLE_API_KEY
)


# --- Prompt Templates ---
# NO CHANGES NEEDED HERE. The prompts remain the same.
base_template = """
You are a helpful AI assistant. Answer the user's question clearly and concisely.
Question: {query}
Answer:
"""
healing_template = """
You are a helpful AI assistant. Your first attempt to answer was not good enough.
Try again, but this time use the following context from your memory to provide a better, more detailed answer.

Relevant Context from Memory:
{context}

Original Question: {query}
Answer:
"""
prompt = PromptTemplate(template=base_template, input_variables=["query"])
healing_prompt = PromptTemplate(template=healing_template, input_variables=["context", "query"])


# --- Self-Healing Logic ---
# NO CHANGES NEEDED IN THE REST OF THE FILE.
# The logic for is_response_unclear() and ask_agent() remains identical
# because LangChain abstracts away the specific model provider.
MAX_ATTEMPTS = 3

def is_response_unclear(response: str) -> bool:
    # ... (code remains the same) ...
    response_lower = response.lower().strip()
    if not response_lower or len(response_lower.split()) < 3:
        return True
    
    failure_phrases = [
        "i can't", "i'm not able", "i don't know", "i am not programmed",
        "as an ai", "i do not have access", "i cannot answer", "i am unable",
        "i cannot provide", "i am not sure", "i do not know", "i cannot say",
        "i am not capable", "i cannot help", "i cannot assist", "i am not designed",
        "i am not trained", "i am not equipped", "i am not able to assist","i cannot","i don't","i am not",
        "i cannot answer this question", "i am unable to answer this question","i cannot provide an answer", "i am not able to answer this question",
        "i am not sure about that", "i do not have enough information", "i cannot provide a definitive answer",
        "i am not programmed to answer that", "i do not have the capability to answer that",
        "i am not designed to answer that", "i am not trained to answer that","i won't be able to",
    ]
    return any(phrase in response_lower for phrase in failure_phrases)


def ask_agent(query: str) -> dict:
    # ... (code remains the same) ...
    # This entire function works without changes because the `llm.invoke` interface
    # is standardized by LangChain.
    healing_attempts = 0
    response_text = ""
    start_time = time.time()

    for attempt in range(MAX_ATTEMPTS):
        try:
            if attempt == 0:
                print("Attempt 1: Basic prompt with Gemini 1.5 Flash")
                chain = prompt | llm
                response = chain.invoke({"query": query})
                response_text = response.content
            
            elif attempt == 1:
                print("Attempt 2: Re-prompting with context from memory")
                healing_attempts += 1
                context = memory.vector_memory.get_relevant_memories(query)
                chain = healing_prompt | llm
                response = chain.invoke({"context": "\n".join(context), "query": query})
                response_text = response.content
            
            elif attempt == 2:
                print("Attempt 3: Using fallback model configuration")
                healing_attempts += 1
                context = memory.vector_memory.get_relevant_memories(query)
                chain = healing_prompt | fallback_llm
                response = chain.invoke({"context": "\n".join(context), "query": query})
                response_text = response.content

            if not is_response_unclear(response_text):
                duration = time.time() - start_time
                confidence = 1.0 - (healing_attempts / MAX_ATTEMPTS)
                feedback.log_interaction(query, response_text, confidence, healing_attempts, success=True)
                return {
                    "answer": response_text,
                    "healing_attempts": healing_attempts,
                    "confidence": confidence,
                    "duration_seconds": round(duration, 2)
                }

        except Exception as e:
            print(f"An error occurred during attempt {attempt + 1}: {e}")
            response_text = f"An internal error occurred: {e}"

    duration = time.time() - start_time
    feedback.log_interaction(query, response_text, 0.0, healing_attempts, success=False)
    return {
        "answer": response_text or "I am unable to answer this question after multiple attempts.",
        "healing_attempts": healing_attempts,
        "confidence": 0.0,
        "duration_seconds": round(duration, 2)
    }