# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 11:18:17 2024

@author: akome
"""

# main.py

import os
import sys
import logging
import pickle
import faiss
import numpy as np
from together import Together
from Scripts.enhance_response import enhance_answer  # Import enhance_answer

# Import utility functions
from Scripts.utils import (
    file_exists,
    split_text_by_headlines,
    embed_text,
    retrieve_documents
)

# Setup logging
def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,  # Set logging level to DEBUG for detailed logs
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

setup_logging()

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # V3/
SCRIPTS_DIR = os.path.join(BASE_DIR, 'Scripts')
DATA_DIR = os.path.join(BASE_DIR, 'Data')  # Data directory

OUTPUT_TEXT_PATH = os.path.join(SCRIPTS_DIR, "extracted_text.txt")
OUTPUT_EMBEDDINGS_PATH = os.path.join(SCRIPTS_DIR, "document_embeddings.pkl")
DOCUMENTS_PATH = os.path.join(SCRIPTS_DIR, "documents.pkl")
INDEX_PATH = os.path.join(SCRIPTS_DIR, "faiss_index.index")

# Initialize Together client
API_KEY = os.environ.get("TOGETHER_API_KEY")
if not API_KEY:
    logging.error("TOGETHER_API_KEY not found in environment variables.")
    sys.exit(1)
client = Together(api_key=API_KEY)

# Initialize variables
try:
    # Load or extract text
    if file_exists(OUTPUT_TEXT_PATH):
        with open(OUTPUT_TEXT_PATH, "r", encoding="utf-8") as f:
            extracted_text = f.read()
        logging.info(f"Loaded extracted text from {OUTPUT_TEXT_PATH}")
    else:
        logging.error(f"Extracted text file not found at {OUTPUT_TEXT_PATH}")
        sys.exit(1)

    # Split the extracted text into sections based on headlines
    doc_chunks = split_text_by_headlines(extracted_text)
    logging.info(f"Split text into {len(doc_chunks)} sections based on headlines")

    # Optionally, print the first few sections for verification
    for idx, section in enumerate(doc_chunks[:5]):
        logging.debug(f"Section {idx + 1}:\n{section}\n{'-' * 40}")

    # Load or save embeddings
    if file_exists(OUTPUT_EMBEDDINGS_PATH):
        with open(OUTPUT_EMBEDDINGS_PATH, "rb") as f:
            document_embeddings = pickle.load(f)
        logging.info(f"Loaded document embeddings from {OUTPUT_EMBEDDINGS_PATH}")
    else:
        # Generate embeddings for doc_chunks
        document_embeddings = embed_text(doc_chunks)
        # Save embeddings
        with open(OUTPUT_EMBEDDINGS_PATH, "wb") as f:
            pickle.dump(document_embeddings, f)
        logging.info(f"Saved document embeddings to {OUTPUT_EMBEDDINGS_PATH}")

    # Load or create FAISS index
    if file_exists(INDEX_PATH) and file_exists(DOCUMENTS_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(DOCUMENTS_PATH, "rb") as f:
            documents = pickle.load(f)
        logging.info(f"Loaded FAISS index and documents.")
    else:
        # Create FAISS index and save documents
        dimension = document_embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(document_embeddings)
        faiss.write_index(index, INDEX_PATH)
        with open(DOCUMENTS_PATH, "wb") as f:
            pickle.dump(doc_chunks, f)
        logging.info(f"Created FAISS index and saved documents.")

except Exception as e:
    logging.error(f"Error during initialization: {e}")
    sys.exit(1)  # Exit if initialization fails

def generate_response(query, history=None, enhance=False):
    retrieved_docs = retrieve_documents(query, k=3)
    if not retrieved_docs:
        logging.error("No documents retrieved.")
        return "I'm sorry, I couldn't find any information related to your query."

    # Combine retrieved documents into context
    combined_context = " ".join(retrieved_docs)
    # Truncate context to fit model's context window
    max_context_length = 2000  # Adjust based on your model's limits
    context = combined_context[:max_context_length]

    # Build the messages list
    messages = []

    # Include instructions within the user's message
    instructions = (
        "You are an assistant that provides information based on the ESUR guidelines. "
        "Provide clear and concise answers, citing chapters or pages when possible."
    )

    # Build conversation history
    if history:
        # Filter out any entries where bot_response is not None
        filtered_history = [(u, b) for u, b in history if b is not None]
        # Limit history to the last 3 exchanges
        max_history = 3
        recent_history = filtered_history[-max_history:]
        for user_msg, bot_response in recent_history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": bot_response})

    # Add the current user query and context
    user_content = f"{instructions}\n\nUser query: {query}\n\nContext:\n{context}"
    messages.append({"role": "user", "content": user_content})

    # Log messages for debugging
    logging.debug("Messages sent to the model:")
    for msg in messages:
        logging.debug(f"{msg['role']}: {msg['content']}")

    # Make the API call
    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",  # Adjust to your model
            messages=messages,
            max_tokens=512
        )
        if response and response.choices:
            assistant_reply = response.choices[0].message.content.strip()

            if enhance:
                logging.debug("Enhancement requested. Enhancing the answer...")
                # Use enhance_answer and get detailed information
                enhancement_result = enhance_answer(query, retrieved_docs, assistant_reply)
                return enhancement_result
            else:
                return assistant_reply
        else:
            logging.error("Empty response from the model.")
            return "I'm sorry, I couldn't generate a response."
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "I'm sorry, there was an error processing your request."

