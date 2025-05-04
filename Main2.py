# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 11:08:22 2024

@author: akome
"""

import os
import sys
import logging
import pickle
import faiss
from together import Together

# Setup logging
logging.basicConfig(level=logging.INFO)

# Update sys.path for module imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'Scripts'))

# Import custom functions
from extractPDF import extract_text
from embed_texts import embed_text, save_embeddings
from create_index import create_faiss_index

# Define paths using os.path.join
base_dir = os.path.dirname(os.path.abspath(__file__))
scripts_dir = os.path.join(base_dir, 'Scripts')

pdf_path = os.path.join(base_dir, "ESUR.pdf")
output_text_path = os.path.join(scripts_dir, "extracted_text.txt")
output_embeddings_path = os.path.join(scripts_dir, "document_embeddings.pkl")
documents_path = os.path.join(scripts_dir, "documents.pkl")
index_path = os.path.join(scripts_dir, "faiss_index.index")

# Function to check if file exists
def file_exists(file_path):
    return os.path.exists(file_path)

# Load or extract text
if file_exists(output_text_path):
    try:
        with open(output_text_path, "r", encoding="utf-8") as f:
            doc_txt = f.read().split('\n\n')
        logging.info(f"Loaded extracted text from {output_text_path}")
    except Exception as e:
        logging.error(f"Error reading {output_text_path}: {e}")
else:
    doc_txt = extract_text(pdf_path, output_text_path)

# Load or save embeddings
if file_exists(output_embeddings_path): 
    try:
        with open(output_embeddings_path, "rb") as f:
            document_embeddings = pickle.load(f)
        logging.info(f"Loaded document embeddings from {output_embeddings_path}")
    except Exception as e:
        logging.error(f"Error loading embeddings: {e}")
else:
    document_embeddings = save_embeddings(doc_txt, output_embeddings_path)

# Load or create FAISS index
if file_exists(index_path) and file_exists(documents_path):
    try:
        index = faiss.read_index(index_path)
        with open(documents_path, "rb") as f:
            documents = pickle.load(f)
        logging.info(f"Loaded FAISS index and documents.")
    except Exception as e:
        logging.error(f"Error loading index or documents: {e}")
else:
    create_faiss_index(document_embeddings, doc_txt, index_path, documents_path)
    index = faiss.read_index(index_path)
    with open(documents_path, "rb") as f:
        documents = pickle.load(f)

# Initialize Together client
api_key = os.environ.get("TOGETHER_API_KEY")
if not api_key:
    logging.error("TOGETHER_API_KEY not found in environment variables.")
    sys.exit(1)
client = Together(api_key=api_key)

# Retrieval function
def retrieve_documents(query, k=5):
    query_embedding = embed_text([query])
    _, I = index.search(query_embedding, k)
    return [documents[i] for i in I[0]]

# Response generation function
def generate_response(query):
    retrieved_docs = retrieve_documents(query)
    context = " ".join(retrieved_docs)[:2048]  # Adjust context length as needed
    instructions = (
        "Use the context to answer the question to the best of your ability. "
        "Provide citations using chapters/pages if possible.\n"
    )
    input_text = f"{instructions}User query: {query}\nContext: {context}"
    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-2-70b-chat-hf",
            messages=[{"role": "user", "content": input_text}],
            max_tokens=512
        )
        if response and response.choices:
            return response.choices[0].message.content
        else:
            logging.error("Empty response from the model.")
            return "I'm sorry, I couldn't generate a response."
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "I'm sorry, there was an error processing your request."
