# File: backend/app/memory.py

import faiss
# --- BEFORE ---
# from langchain.vectorstores import FAISS
# from langchain_openai import OpenAIEmbeddings
# from langchain.docstore.document import Document
# import numpy as np
# from . import config # Added import for config

# --- AFTER ---
# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings # <-- CHANGE THIS IMPORT
from langchain.docstore.document import Document
import numpy as np
from . import config # Make sure config is imported

# A simple in-memory store for the FAISS index
class VectorMemory:
    """Manages the agent's vector memory using FAISS."""
    def __init__(self, embedding_provider):
        self.embedding_provider = embedding_provider
        
        # --- CRITICAL CHANGE ---
        # OpenAI's embeddings are 1536 dimensional.
        # Google's new embedding model is 768 dimensional.
        # We MUST change this number or FAISS will fail.
        # self.index = faiss.IndexFlatL2(1536) # <-- BEFORE
        self.index = faiss.IndexFlatL2(768) # <-- AFTER (for "models/embedding-001")
        
        self.docstore = {} 
        self.doc_id_counter = 0

    # ... The rest of the class (add_memory, get_relevant_memories) has NO CHANGES ...
    def add_memory(self, text: str):
        # ... (code remains the same) ...
        """Adds a new piece of text to the memory."""
        try:
            embedding = self.embedding_provider.embed_query(text)
            vector = np.array([embedding], dtype="float32")
            self.index.add(vector)
            # Store the document text with a new ID
            self.docstore[self.doc_id_counter] = Document(page_content=text)
            self.doc_id_counter += 1
            print(f"🧠 Added memory: '{text}'")
            return True
        except Exception as e:
            print(f"Error adding memory: {e}")
            return False
    def get_relevant_memories(self, query: str, k: int = 2) -> list[str]:
        # ... (code remains the same) ...
        """
        Retrieves the most relevant memories for a given query.
        
        Edge Case Handled: Failed vector similarity lookups.
        """
        if self.index.ntotal == 0:
            return [] # No memories to search
            
        try:
            query_embedding = self.embedding_provider.embed_query(query)
            query_vector = np.array([query_embedding], dtype="float32")
            
            # Search the index
            distances, indices = self.index.search(query_vector, k)
            
            # Retrieve the documents
            relevant_docs = [self.docstore[i].page_content for i in indices[0] if i in self.docstore]
            print(f"🧠 Retrieved memories: {relevant_docs}")
            return relevant_docs
        except Exception as e:
            print(f"Error during vector similarity lookup: {e}")
            return [] # Return empty list on failure

# --- Initialization ---

# --- BEFORE ---
# embedding_provider = OpenAIEmbeddings(api_key=config.OPENAI_API_KEY)
# vector_memory = VectorMemory(embedding_provider)
# ...

# --- AFTER ---
# Use the Google embedding model
embedding_provider = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", 
    google_api_key=config.GOOGLE_API_KEY
)
vector_memory = VectorMemory(embedding_provider)


# Let's pre-load our agent with some "good" examples (few-shot injections)
# NO CHANGES NEEDED HERE
vector_memory.add_memory("The user is asking for help building a system. Your primary goal is to be a helpful assistant.")
vector_memory.add_memory("A 'self-healing' system automatically detects and recovers from failures.")