# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 11:31:01 2024

@author: akome
"""

# Scripts/utils.py
import os
import re
import logging
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer

def file_exists(file_path):
    """
    Check if a file exists at the given path.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.exists(file_path)

def setup_logging(level=logging.DEBUG):
    """
    Set up the logging configuration.

    Args:
        level (int, optional): Logging level. Defaults to logging.DEBUG.
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

def split_text_into_chunks(text, chunk_size=250, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def split_text_into_sections(text):
    # Regular expression pattern for headings (adjust as needed)
    pattern = r'(Chapter\s\d+|Section\s\d+|\n[A-Z][^\n]+(?:\n|$))'

    # Find all headings
    headings = re.findall(pattern, text)
    # Split text by headings
    splits = re.split(pattern, text)
    # Combine headings with their corresponding sections
    sections = []
    for i in range(1, len(splits)):
        section_title = splits[i - 1].strip()
        section_content = splits[i].strip()
        if section_content:
            sections.append(f"{section_title}\n{section_content}")
    return sections

def split_text_by_headlines(text):
    """
    Splits the text into sections based on headlines.
    Headlines are detected based on specific patterns.
    """
    headline_pattern = re.compile(r"""
        (?:
            ^[A-Z][A-Z\s\d\.\-:,]{2,}$      # Lines in uppercase (with possible numbers, dots, hyphens, colons)
            |
            ^(?:\d+\.)+\s.*$                # Lines starting with numbering like '1.', '1.1.', '2.3.1'
        )
        """, re.MULTILINE | re.VERBOSE)

    splits = re.split(headline_pattern, text)
    headlines = re.findall(headline_pattern, text)

    sections = []
    for idx, headline in enumerate(headlines):
        if idx < len(splits):
            content = splits[idx + 1].strip() if idx + 1 < len(splits) else ''
            headline = headline.strip()
            if content:
                section = f"{headline}\n{content}"
            else:
                section = headline
            sections.append(section)

    remaining_content = splits[len(headlines) + 1:] if len(splits) > len(headlines) + 1 else []
    for content in remaining_content:
        content = content.strip()
        if content:
            sections.append(content)

    return sections

# -------------------------------------
# Model and Global Variables
# -------------------------------------

embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

documents = None  # Will be set by main.py
index = None      # Will be set by main.py

def set_documents(docs):
    """
    Store the documents globally.
    """
    global documents
    documents = docs

def set_index(idx):
    """
    Store the FAISS index globally.
    """
    global index
    index = idx

# -------------------------------------
# Embedding and Retrieval
# -------------------------------------

def embed_text(text_list):
    embeddings = embedding_model.encode(text_list, convert_to_numpy=True)
    # Normalize embeddings
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / norms
    return embeddings.astype('float32')  # Ensure embeddings are float32 for FAISS

def retrieve_documents(query, k=3, return_details=False):
    """
    Retrieves the top-k most relevant documents for a given query.

    Args:
        query (str): The query string.
        k (int): Number of top documents to retrieve.
        return_details (bool): Whether to return indices and distances along with the documents.

    Returns:
        list: A list of retrieved document chunks if return_details=False
        tuple: (retrieved_chunks, indices, distances) if return_details=True
    """
    if documents is None or index is None:
        logging.error("Documents or index have not been set. Please call set_documents and set_index first.")
        if return_details:
            return [], [], []
        return []

    try:
        logging.debug(f"Starting document retrieval for query: {query}")
        query_embedding = embed_text([query])

        logging.debug(f"Query embedding shape: {query_embedding.shape}")

        # Retrieve top k documents
        D, I = index.search(query_embedding, k)

        logging.debug(f"Indices returned: {I}")
        logging.debug(f"Distances: {D}")

        retrieved_indices = [i for i in I[0] if i >= 0]
        retrieved_chunks = [documents[i] for i in retrieved_indices]
        distances = D[0].tolist()

        # Log the retrieved documents
        logging.debug("Retrieved Documents:")
        for idx_val, doc in zip(retrieved_indices, retrieved_chunks):
            logging.debug(f"Document index: {idx_val}, Content: {doc[:200]}")

        if return_details:
            return retrieved_chunks, retrieved_indices, distances
        else:
            return retrieved_chunks
    except Exception as e:
        logging.error(f"Error in retrieve_documents: {e}")
        if return_details:
            return [], [], []
        return []

