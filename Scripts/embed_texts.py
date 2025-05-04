# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 10:55:42 2024

@author: akome
"""

# embed_texts.py
from sentence_transformers import SentenceTransformer
import pickle
import os

# Load pre-trained SentenceTransformer model for embeddings
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

def embed_text(text_list):
    embeddings = embedding_model.encode(text_list, convert_to_numpy=True)
    # Normalize embeddings
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / norms
    return embeddings

def save_embeddings(doc_txt, output_embeddings_path):
    document_embeddings = embed_text(doc_txt)

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_embeddings_path), exist_ok=True)

    # Save the embeddings to a file
    with open(output_embeddings_path, "wb") as f:
        pickle.dump(document_embeddings, f)

    print(f"Document embeddings saved to {output_embeddings_path}")

    return document_embeddings

# Example usage for testing
if __name__ == "__main__":
    doc_txt = ["Example text"]
    output_embeddings_path = "C:/Users/akome/Desktop/RAG/V3/Scripts/document_embeddings.pkl"
    save_embeddings(doc_txt, output_embeddings_path)
