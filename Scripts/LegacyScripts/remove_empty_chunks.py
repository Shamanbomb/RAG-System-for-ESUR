# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 15:12:38 2025

@author: akome
"""

import pickle

# Load the documents.pkl file
with open('documents.pkl', 'rb') as f:
    data = pickle.load(f)

# Print the number of chunks before removal
print(f"Original number of chunks: {len(data)}")

# Remove empty chunks
data = [chunk for chunk in data if chunk.strip()]

# Print the number of chunks after removal
print(f"Updated number of chunks: {len(data)}")

# Save the cleaned data back to documents.pkl
with open('documents.pkl', 'wb') as f:
    pickle.dump(data, f)

print("Empty chunks removed successfully. Updated documents.pkl has been saved.")
