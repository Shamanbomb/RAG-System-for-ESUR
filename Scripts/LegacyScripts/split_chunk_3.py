# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 14:46:53 2025

@author: akome
"""
import pickle

# Load the documents.pkl file
with open('documents.pkl', 'rb') as f:
    data = pickle.load(f)

# Print original number of chunks
print(f"Original number of chunks: {len(data)}")

# The chunk to be split (Chunk 5 → index 4 in 0-based Python indexing)
chunk_index = 4  
chunk_text = data[chunk_index]

# Define the **exact split points** based on your instructions
split_markers = [
    "reliable diagnosis).",
    "occur during anaphylaxis.",
    "car or operate machinery.",
    "(0.15 mg) intramuscularly",  # First occurrence
    "(0.15 mg) intramuscularly",  # Second occurrence
    "(0.15 mg) intramuscularly",  # Third occurrence
    "treat as for anaphylaxis."
]

# Find the **exact positions** of each marker in the text
positions = []
for marker in split_markers:
    pos = chunk_text.find(marker)
    if pos != -1:
        positions.append((pos + len(marker), marker))  # Store end position of each marker

# Sort positions to ensure they are in order
positions.sort()

# If no markers were found, exit
if not positions:
    print("No valid split markers found. Check the text formatting.")
    exit()

# Split the text at the detected positions
split_chunks = []
previous_position = 0

for pos, marker in positions:
    # Extract content from previous position to the current marker
    split_chunks.append(chunk_text[previous_position:pos].strip())
    previous_position = pos

# Add the last remaining section
split_chunks.append(chunk_text[previous_position:].strip())

# Remove the original Chunk 5 and insert the newly split sections
data = data[:chunk_index] + split_chunks + data[chunk_index + 1:]

# Print updated number of chunks
print(f"Updated number of chunks: {len(data)}")

# Save the modified data back to documents.pkl
with open('documents.pkl', 'wb') as f:
    pickle.dump(data, f)

print("Updated documents.pkl has been saved successfully.")
