# File: backend/app/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- BEFORE ---
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# MONGO_URI = os.getenv("MONGO_URI")
# ...

# --- AFTER ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Keep for embeddings for now
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # <-- ADD THIS LINE
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "ai_system_logs")

# Simple check to ensure that environment variables are set
if not GOOGLE_API_KEY or not MONGO_URI: # <-- UPDATE THIS CHECK
    raise ValueError("Missing critical environment variables: GOOGLE_API_KEY or MONGO_URI")