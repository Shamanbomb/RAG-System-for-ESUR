# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 15:04:23 2024

@author: akome
"""

# extractPDF.py

import os
import sys
import logging
import fitz  # PyMuPDF
import pandas as pd
import camelot
import re
import shutil
import tempfile

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

def extract_text_and_tables(pdf_path, output_text_path):
    setup_logging()
    logging.info(f"Starting extraction from {pdf_path}")

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_text_path), exist_ok=True)

    doc = fitz.open(pdf_path)
    all_text = ""
    temp_dir = tempfile.mkdtemp()

    try:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            logging.info(f"Processing page {page_num + 1}")
            page_text_blocks = extract_page_text(page)
            page_table_blocks = extract_page_tables(pdf_path, page_num)
            # Merge text and tables based on positions
            combined_content = merge_blocks(page_text_blocks, page_table_blocks)
            all_text += combined_content + "\n\n"
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

    # Save the extracted text to a file
    with open(output_text_path, "w", encoding="utf-8") as f:
        f.write(all_text)

    logging.info(f"Extraction completed. Text saved to {output_text_path}")

    return all_text

def extract_page_text(page):
    blocks = page.get_text("dict")["blocks"]

    # Extract text blocks with positions
    text_blocks = []
    for block in blocks:
        if block["type"] == 0:  # Text block
            bbox = block["bbox"]
            block_text = ""
            for line in block["lines"]:
                for span in line["spans"]:
                    block_text += span["text"]
            text_blocks.append({
                "text": block_text.strip(),
                "bbox": bbox,
                "y0": bbox[1],  # Top coordinate
                "x0": bbox[0],  # Left coordinate
            })

    # Sort blocks by y0 (top coordinate), then x0 (left coordinate)
    text_blocks.sort(key=lambda b: (b["y0"], b["x0"]))
    return text_blocks

def extract_page_tables(pdf_path, page_num):
    # Extract tables using Camelot
    try:
        tables = camelot.read_pdf(
            pdf_path,
            pages=str(page_num + 1),  # Camelot pages are 1-indexed
            flavor='stream',  # Use 'stream' flavor for PDFs without ruling lines
        )
        page_tables = []
        for idx, table in enumerate(tables):
            df = table.df
            table_text = df.to_csv(sep='\t', index=False, header=False)
            bbox = table._bbox  # Bounding box of the table (x1, y1, x2, y2)
            # Adjust y0 to match PyMuPDF coordinate system
            page_height = get_page_height(pdf_path, page_num)
            y0 = page_height - bbox[1]  # Convert y1 from Camelot to y0 in PyMuPDF
            x0 = bbox[0]  # x0 is the same in both coordinate systems

            page_tables.append({
                "text": f"[TABLE]\n{table_text.strip()}\n[/TABLE]",
                "bbox": (x0, y0, bbox[2], bbox[3]),
                "y0": y0,
                "x0": x0,
            })
        return page_tables
    except Exception as e:
        logging.warning(f"Failed to extract tables on page {page_num + 1}: {e}")
        return []

def get_page_height(pdf_path, page_num):
    with fitz.open(pdf_path) as doc:
        page = doc.load_page(page_num)
        return page.rect.height

def merge_blocks(text_blocks, table_blocks):
    # Combine text blocks and table blocks based on positions
    all_blocks = text_blocks + table_blocks

    # Sort blocks by y0 (top coordinate), then x0 (left coordinate)
    all_blocks.sort(key=lambda b: (b["y0"], b["x0"]))

    page_content = ""
    for block in all_blocks:
        text = block["text"]
        if is_heading(text):
            page_content += f"\n\n{text}\n\n"
        elif is_list_item(text):
            page_content += f"- {text}\n"
        elif "[TABLE]" in text:
            page_content += f"\n{text}\n"
        else:
            page_content += text + " "

    return page_content.strip()

def is_heading(text):
    """
    Determine if a block of text is a heading based on heuristics.
    Adjust this function based on the specific formatting of your PDF.
    """
    # Example heuristic: check if text is uppercase and short
    if text.isupper() and len(text.split()) < 10:
        return True
    # Check if text starts with a section number (e.g., '1.', '1.1', '2.3.1')
    if re.match(r'^(\d+\.)+(\d+)?\s', text):
        return True
    # Check for bold or larger font sizes (if needed)
    return False

def is_list_item(text):
    """
    Determine if a line is a list item.
    """
    if text.strip().startswith(('-', '*', '•')):
        return True
    return False

# Example usage
if __name__ == "__main__":
    # Adjust paths based on your directory structure
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory containing extractPDF.py
    SCRIPTS_DIR = BASE_DIR  # Since extractPDF.py is in the Scripts directory
    PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
    DATA_DIR = os.path.join(PROJECT_DIR, 'Data')  # Data directory containing ESUR.pdf
    OUTPUT_DIR = SCRIPTS_DIR  # Output files will be saved in the Scripts directory

    PDF_FILENAME = "ESUR.pdf"
    OUTPUT_TEXT_FILENAME = "extracted_text.txt"

    pdf_path = os.path.join(DATA_DIR, PDF_FILENAME)
    output_text_path = os.path.join(OUTPUT_DIR, OUTPUT_TEXT_FILENAME)

    # Ensure the Data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logging.info(f"Created Data directory at {DATA_DIR}")

    # Check if the PDF file exists
    if not os.path.isfile(pdf_path):
        logging.error(f"PDF file not found at {pdf_path}")
        sys.exit(1)

    extract_text_and_tables(pdf_path, output_text_path)

