# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 16:51:16 2025

@author: akome
"""

import pickle

# Load the documents.pkl file
with open('documents.pkl', 'rb') as f:
    data = pickle.load(f)

# Print original number of chunks
print(f"Original number of chunks: {len(data)}")

# Define chunks to combine, adjusting for 1-based indexing (subtract 1)
chunks_to_combine = [
    (14 - 1, 15 - 1),
    (32 - 1, 34 - 1)# Combine chunks 3 to 6 (inclusive)
    
]

# Create a new list to store modified chunks
new_data = []
skip_indices = set()  # Track which indices have been combined

for idx, chunk in enumerate(data):
    if idx in skip_indices:
        continue

    for start, end in chunks_to_combine:
        if idx == start:
            # Combine the range of chunks
            combined_chunk = " ".join(data[start:end + 1])
            new_data.append(combined_chunk)
            skip_indices.update(range(start, end + 1))
            break
    else:
        # Add chunk if not part of the merged ranges
        new_data.append(chunk)

# Print updated number of chunks
print(f"Updated number of chunks: {len(new_data)}")

# Save the modified data back to documents.pkl
with open('documents.pkl', 'wb') as f:
    pickle.dump(new_data, f)

print("Updated documents.pkl has been saved successfully.")
