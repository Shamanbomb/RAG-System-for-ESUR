# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 10:02:53 2024

@author: akome
"""

import os
import pdf2image
import pytesseract

def extract_text(pdf_path, output_text_path):
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_text_path), exist_ok=True)

    # Convert PDF to images
    doc_img = pdf2image.convert_from_path(pdf_path, dpi=300)

    # Extract text from each image
    doc_txt = []
    for page in doc_img:
        text = pytesseract.image_to_string(page)
        doc_txt.append(text)

    # Save the extracted text to a file
    with open(output_text_path, "w", encoding="utf-8") as f:
        for page_text in doc_txt:
            f.write(page_text)
            f.write("\n\n")  # Add some spacing between pages

    print(f"Extracted text saved to {output_text_path}")

    return doc_txt

# Example usage
if __name__ == "__main__":
    pdf_path = "C:/Users/akome/Desktop/RAG/ESUR.pdf"
    output_text_path = "C:/Users/akome/Desktop/RAG/V3/Scripts/extracted_text.txt"
    extract_text(pdf_path, output_text_path)