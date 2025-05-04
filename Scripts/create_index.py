# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 10:56:11 2024

@author: akome
"""

# create_index.py
import faiss
import pickle
import os
import numpy as np

def create_faiss_index(document_embeddings, documents, index_path, documents_path):
    # Convert embeddings to float32 if they are not already
    if document_embeddings.dtype != np.float32:
        document_embeddings = document_embeddings.astype('float32')

    # Create and train the FAISS index
    index = faiss.IndexFlatIP(document_embeddings.shape[1])
    index.add(document_embeddings)

    # Ensure the output directories exist
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    os.makedirs(os.path.dirname(documents_path), exist_ok=True)

    # Save the index and documents
    faiss.write_index(index, index_path)
    with open(documents_path, "wb") as f:
        pickle.dump(documents, f)

    print(f"FAISS index saved to {index_path} and documents saved to {documents_path}")

