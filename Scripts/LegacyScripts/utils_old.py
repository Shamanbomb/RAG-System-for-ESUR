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

import logging

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

import re

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
    # Define the regex pattern for headlines using non-capturing groups
    headline_pattern = re.compile(r"""
        (?:
            ^[A-Z][A-Z\s\d\.\-:,]{2,}$      # Lines in uppercase (with possible numbers, dots, hyphens, colons)
            |
            ^(?:\d+\.)+\s.*$                # Lines starting with numbering like '1.', '1.1.', '2.3.1'
        )
        """, re.MULTILINE | re.VERBOSE)

    # Split the text based on the headline pattern
    splits = re.split(headline_pattern, text)
    # Find all headlines
    headlines = re.findall(headline_pattern, text)

    sections = []

    # Pair each headline with its corresponding content
    for idx, headline in enumerate(headlines):
        # Get the content following the headline
        if idx < len(splits):
            content = splits[idx + 1].strip() if idx + 1 < len(splits) else ''
            headline = headline.strip()
            if content:
                section = f"{headline}\n{content}"
            else:
                section = headline
            sections.append(section)

    # Handle any remaining content without a headline
    remaining_content = splits[len(headlines) + 1:] if len(splits) > len(headlines) + 1 else []
    for content in remaining_content:
        content = content.strip()
        if content:
            sections.append(content)

    return sections

# Initialize the embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

def embed_text(text_list):
    embeddings = embedding_model.encode(text_list, convert_to_numpy=True)
    # Normalize embeddings
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / norms
    return embeddings.astype('float32')  # Ensure embeddings are float32 for FAISS

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Scripts/
V3_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))  # V3/
SCRIPTS_DIR = BASE_DIR
DOCUMENTS_PATH = os.path.join(SCRIPTS_DIR, "documents.pkl")
INDEX_PATH = os.path.join(SCRIPTS_DIR, "faiss_index.index")

# Load documents and index
with open(DOCUMENTS_PATH, "rb") as f:
    documents = pickle.load(f)
index = faiss.read_index(INDEX_PATH)

def retrieve_documents(query, k=3, return_details=False):
    """
    Retrieves the top-k most relevant documents for a given query.

    Args:
        query (str): The query string.
        k (int): Number of top documents to retrieve.
        return_details (bool): Whether to return indices and distances along with the documents.

    Returns:
        list: A list of retrieved document chunks if return_details is False.
        tuple: (retrieved_chunks, indices, distances) if return_details is True.
    """
    try:
        logging.debug(f"Starting document retrieval for query: {query}")
        query_embedding = embed_text([query])

        logging.debug(f"Query embedding shape: {query_embedding.shape}")

        # Retrieve top k documents
        D, I = index.search(query_embedding, k)

        logging.debug(f"Indices returned: {I}")
        logging.debug(f"Distances: {D}")

        # Filter out invalid indices
        retrieved_indices = [i for i in I[0] if i >= 0]

        # Retrieve the corresponding document chunks
        retrieved_chunks = [documents[i] for i in retrieved_indices]
        distances = D[0].tolist()

        # Log the retrieved documents
        logging.debug("Retrieved Documents:")
        for idx, doc in zip(retrieved_indices, retrieved_chunks):
            logging.debug(f"Document index: {idx}, Content: {doc[:200]}")

        if return_details:
            return retrieved_chunks, retrieved_indices, distances
        else:
            return retrieved_chunks
    except Exception as e:
        logging.error(f"Error in retrieve_documents: {e}")
        if return_details:
            return [], [], []
        return []
