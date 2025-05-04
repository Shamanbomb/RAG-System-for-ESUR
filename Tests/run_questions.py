# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 22:14:14 2024

@author: akome
"""
# run_questions.py

import os
import sys
import logging
import csv
from datetime import datetime
import time
import re  # Import the re module for regular expressions
import json  # Import the json module

# Adjust sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))  # Tests/
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))  # V3/
sys.path.append(parent_dir)

# Now import from main.py
from main import generate_response

# Setup logging
def setup_logging():
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(current_dir, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Create a unique log file name based on timestamp
    log_filename = datetime.now().strftime('run_questions_%Y%m%d_%H%M%S.log')
    log_filepath = os.path.join(logs_dir, log_filename)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filepath),
            logging.StreamHandler(sys.stdout)
        ]
    )

setup_logging()

# Read the list of questions from question_list.txt
questions_file = os.path.join(current_dir, 'question_list.txt')
if not os.path.isfile(questions_file):
    logging.error(f"Questions file '{questions_file}' not found.")
    sys.exit(1)

with open(questions_file, 'r', encoding='utf-8') as f:
    # Read lines and strip whitespace
    lines = [line.strip() for line in f if line.strip()]
    # Remove numbering prefixes using regex
    questions = [re.sub(r'^\d+\.\s*', '', line) for line in lines]

if not questions:
    logging.error(f"No questions found in '{questions_file}'.")
    sys.exit(1)

# List to hold the results
results = []

# Run the questions through the system
for idx, question in enumerate(questions, start=1):
    logging.info(f"Processing question {idx}/{len(questions)}: {question}")
    try:
        start_time = time.time()
        # Pass enhance=True to generate enhanced answers and retrieve chunks
        response = generate_response(question, enhance=True)
        end_time = time.time()
        time_taken = end_time - start_time
        logging.info(f"Time taken: {time_taken:.2f} seconds")

        # Extract information from the response
        if isinstance(response, dict):
            original_answer = response.get('original_answer', '')
            evaluation = response.get('evaluation', {})
            final_answer = response.get('final_answer', '')
            expanded_keywords = response.get('expanded_keywords', '')
            retrieved_chunks = response.get('retrieved_chunks', [])
            retrieved_indices = response.get('retrieved_indices', [])
            distances = response.get('distances', [])
            enhanced_query = response.get('query', question)  # Use the original question if no query is returned
        else:
            # If response is not a dict, enhancement did not occur
            original_answer = response
            evaluation = {}
            final_answer = response
            expanded_keywords = ''
            retrieved_chunks = []
            retrieved_indices = []
            distances = []
            enhanced_query = question

        logging.info(f"Original Answer:\n{original_answer}\n")
        logging.info(f"Evaluation:\n{evaluation}\n")
        logging.info(f"Final Answer:\n{final_answer}\n")
        if expanded_keywords:
            logging.info(f"Expanded Keywords:\n{expanded_keywords}\n")
        logging.info(f"Retrieved Chunks:\n{retrieved_chunks}\n")
        logging.info(f"Retrieved Indices:\n{retrieved_indices}\n")
        logging.info(f"Distances:\n{distances}\n")
        logging.info(f"Enhanced Query:\n{enhanced_query}\n")

        # Append to results list
        results.append({
            'Question': question,
            'EnhancedQuery': enhanced_query,
            'OriginalAnswer': original_answer,
            'Evaluation': json.dumps(evaluation),
            'FinalAnswer': final_answer,
            'ExpandedKeywords': expanded_keywords,
            'RetrievedChunks': json.dumps(retrieved_chunks),
            'RetrievedIndices': json.dumps(retrieved_indices),
            'Distances': json.dumps(distances),
            'TimeTakenSeconds': round(time_taken, 2)
        })
    except Exception as e:
        logging.error(f"Error processing question '{question}': {e}")
        # Append error information to results
        results.append({
            'Question': question,
            'EnhancedQuery': '',
            'OriginalAnswer': '',
            'Evaluation': '',
            'FinalAnswer': f"Error: {e}",
            'ExpandedKeywords': '',
            'RetrievedChunks': '',
            'RetrievedIndices': '',
            'Distances': '',
            'TimeTakenSeconds': None
        })

# After processing all questions, write the results to a .txt file in CSV format
output_filename = datetime.now().strftime('results_%Y%m%d_%H%M%S.txt')
output_filepath = os.path.join(current_dir, output_filename)

# Define the CSV header
fieldnames = [
    'Question', 'EnhancedQuery', 'OriginalAnswer', 'Evaluation',
    'FinalAnswer', 'ExpandedKeywords', 'RetrievedChunks',
    'RetrievedIndices', 'Distances', 'TimeTakenSeconds'
]

def clean_text(text):
    if text is None:
        return ''
    else:
        return text.replace('\n', ' ').replace('\r', ' ').replace(',', ' ')

# Write to the output file
with open(output_filepath, 'w', encoding='utf-8', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write the header
    writer.writeheader()

    # Write each row
    for result in results:
        # Clean up any newlines or commas in the data to prevent CSV formatting issues
        result_cleaned = {
            'Question': clean_text(result['Question']),
            'EnhancedQuery': clean_text(result['EnhancedQuery']),
            'OriginalAnswer': clean_text(result['OriginalAnswer']),
            'Evaluation': clean_text(result['Evaluation']),
            'FinalAnswer': clean_text(result['FinalAnswer']),
            'ExpandedKeywords': clean_text(result['ExpandedKeywords']),
            'RetrievedChunks': clean_text(result['RetrievedChunks']),
            'RetrievedIndices': clean_text(result['RetrievedIndices']),
            'Distances': clean_text(result['Distances']),
            'TimeTakenSeconds': result['TimeTakenSeconds']
        }
        writer.writerow(result_cleaned)

logging.info(f"Results have been written to {output_filename}")


